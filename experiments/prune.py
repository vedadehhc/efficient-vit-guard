import copy
from facenet_pytorch import MTCNN
import torch
import torch.nn as nn

Byte = 8
KiB = 1024 * Byte
MiB = 1024 * KiB
GiB = 1024 * MiB

def get_num_parameters(model: nn.Module, count_nonzero_only=False) -> int:
    """
    calculate the total number of parameters of model
    :param count_nonzero_only: only count nonzero weights
    """
    num_counted_elements = 0
    for param in model.parameters():
        if count_nonzero_only:
            num_counted_elements += param.count_nonzero()
        else:
            num_counted_elements += param.numel()
    return num_counted_elements

def get_model_size(model: nn.Module, data_width=32, count_nonzero_only=False) -> int:
    """
    calculate the model size in bits
    :param data_width: #bits per element
    :param count_nonzero_only: only count nonzero weights
    """
    return get_num_parameters(model, count_nonzero_only) * data_width

def get_sparsity(tensor: torch.Tensor) -> float:
    """
    calculate the sparsity of the given tensor
        sparsity = #zeros / #elements = 1 - #nonzeros / #elements
    """
    return 1 - float(tensor.count_nonzero()) / tensor.numel()
def get_num_channels_to_keep(channels: int, prune_ratio: float) -> int:
    """A function to calculate the number of layers to PRESERVE after pruning
    Note that preserve_rate = 1. - prune_ratio
    """
    ##################### YOUR CODE STARTS HERE #####################
    return round((1- prune_ratio) * channels)
    ##################### YOUR CODE ENDS HERE #####################

@torch.no_grad()
def get_convs(model: nn.Module):
    model = copy.deepcopy(model)  # do not modify the original model
    # fetch all the conv layers from the backbone
    all_convs = [] 
    all_prelus = []

    modules = [(n, m) for (n,m) in model.named_modules()]

    for i, (name, module) in enumerate(modules):
        # print(name)
        if "conv" in name:
            if "_" not in name:
                prelu_name, prelu = modules[i+1]
                print(name, prelu_name)
                all_prelus.append(prelu)
                all_convs.append(module)

    return model, all_convs, all_prelus

@torch.no_grad()
def channel_prune(model: nn.Module,
                  prune_ratio) -> nn.Module:
    """Apply channel pruning to each of the conv layer in the backbone
    Note that for prune_ratio, we can either provide a floating-point number,
    indicating that we use a uniform pruning rate for all layers, or a list of
    numbers to indicate per-layer pruning rate.
    """
    # sanity check of provided prune_ratio
    assert isinstance(prune_ratio, (float, list))
    model, all_convs, all_prelus = get_convs(model)
    
    n_conv = len(all_convs)
    # note that for the ratios, it affects the previous conv output and next
    # conv input, i.e., conv0 - ratio0 - conv1 - ratio1-...
    if isinstance(prune_ratio, list):
        assert len(prune_ratio) == n_conv - 1
    else:  # convert float to list
        prune_ratio = [prune_ratio] * (n_conv - 1)

    # we prune the convs in the backbone with a uniform ratio    
    num_pruned = 0
    # apply pruning. we naively keep the first k channels
    for i_ratio, p_ratio in enumerate(prune_ratio):
        prev_conv = all_convs[i_ratio]
        next_conv = all_convs[i_ratio + 1]
        original_channels = prev_conv.out_channels  # same as next_conv.in_channels
        n_keep = get_num_channels_to_keep(original_channels, p_ratio)

        if prev_conv.weight.shape[0] == next_conv.weight.shape[1]:
            num_pruned += 1
            # prune the output of the previous conv
            prev_conv.weight.set_(prev_conv.weight.detach()[:n_keep])
            prev_conv.bias.set_(prev_conv.bias.detach()[:n_keep])
            all_prelus[i_ratio].weight.set_(all_prelus[i_ratio].weight.detach()[:n_keep])
            
            # prune the input of the next conv (hint: just one line of code)
            ##################### YOUR CODE STARTS HERE #####################
            next_conv.weight.set_(next_conv.weight.detach()[:,:n_keep])
            ##################### YOUR CODE ENDS HERE #####################

    print(f"{num_pruned=}")
    return model

# function to sort the channels from important to non-important
def get_input_channel_importance(weight):
    in_channels = weight.shape[1]
    importances = []
    # compute the importance for each input channel
    for i_c in range(weight.shape[1]):
        channel_weight = weight.detach()[:, i_c]
        ##################### YOUR CODE STARTS HERE #####################
        importance = torch.norm(channel_weight)
        ##################### YOUR CODE ENDS HERE #####################
        importances.append(importance.view(1))
    return torch.cat(importances)

@torch.no_grad()
def apply_channel_sorting(model):
    model, all_convs, all_prelus = get_convs(model)
    
    sorted_channels = 0
    # iterate through conv layers
    for i_conv in range(len(all_convs) - 1):
        # each channel sorting index, we need to apply it to:
        # - the output dimension of the previous conv
        # - the previous BN layer
        # - the input dimension of the next conv (we compute importance here)
        prev_conv = all_convs[i_conv]
        next_conv = all_convs[i_conv + 1]
        # note that we always compute the importance according to input channels
        importance = get_input_channel_importance(next_conv.weight)
        # sorting from large to small
        sort_idx = torch.argsort(importance, descending=True)

        # print(prev_conv.weight.shape, next_conv.weight.shape)

        if prev_conv.weight.shape[0] == next_conv.weight.shape[1]:
            sorted_channels += 1
            # apply to previous conv and its following bn
            prev_conv.weight.copy_(torch.index_select(
                prev_conv.weight.detach(), 0, sort_idx))
            prev_conv.bias.copy_(torch.index_select(
                prev_conv.bias.detach(), 0, sort_idx))
            all_prelus[i_conv].weight.copy_(torch.index_select(
                all_prelus[i_conv].weight.detach(), 0, sort_idx))
            
            # apply to the next conv input (hint: one line of code)
            ##################### YOUR CODE STARTS HERE #####################
            next_conv.weight.copy_(torch.index_select(next_conv.weight.detach(), 1, sort_idx))
            ##################### YOUR CODE ENDS HERE #####################

    print(f"{sorted_channels=}")
    return model

if __name__ == "__main__":

    model = MTCNN()
    dense_model_size = get_model_size(model, count_nonzero_only=True)

    sorted_model = apply_channel_sorting(model)
    pruned_model = channel_prune(sorted_model, 0.5)
    sparse_model_size = get_model_size(pruned_model, count_nonzero_only=True)
    print(f"Sparse model has size={sparse_model_size / MiB:.2f} MiB = {sparse_model_size / dense_model_size * 100:.2f}% of dense model size")
    
    file_path = 'pruned_facenet_before_ft.pt'
    torch.save(pruned_model, file_path)