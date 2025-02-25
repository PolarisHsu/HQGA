from videoqa import *
import dataloader
from build_vocab import Vocabulary
from utils import *
import argparse
import eval_mc
import eval_oe


def main(args):
    n_gpu = args.ngpu
    print(f"{n_gpu} GPU{'' if n_gpu==1 else 's'} to use.")
    mode = args.mode
    if mode == "train":
        batch_size = 32
        num_worker = 4
    else:
        batch_size = 32
        num_worker = 4
    dataset = "nextqa"  # nextqa, msrvtt,tgifqa
    task = ""  # if tgifqa, set task to 'action', 'transition', 'frameqa'
    multi_choice = True  # True for nextqa and tgifqa-action(transition)
    use_bert = True
    spatial = True
    if spatial:
        video_feature_path = f"../datasets/{dataset}/{task}/"
        video_feature_cache = f"../datasets/{dataset}/{task}/"
    else:
        video_feature_path = f"../datasets/{dataset}/"
        video_feature_cache = f"../datasets/{dataset}/cache_resnetnext32/"

    sample_list_path = f"dataset/{dataset}/{task}/"
    vocab = pkload(f"dataset/{dataset}/{task}/vocab.pkl")

    glove_embed = f"dataset/{dataset}/{task}/glove_embed.npy"
    checkpoint_path = f"models/{dataset}/{task}"
    model_type = "HQGA"
    model_prefix = "bert-16c20b-2L05GCN-FCV-AC-VM"

    vis_step = 200
    lr_rate = 1e-4
    epoch_num = 50
    grad_accu_steps = 1

    data_loader = dataloader.QALoader(
        batch_size,
        num_worker,
        video_feature_path,
        video_feature_cache,
        sample_list_path,
        vocab,
        multi_choice,
        use_bert,
        True,
        False,
    )

    train_loader, val_loader = data_loader.run(mode=mode)
    vqa = VideoQA(
        vocab,
        train_loader,
        val_loader,
        glove_embed,
        checkpoint_path,
        model_type,
        model_prefix,
        vis_step,
        lr_rate,
        batch_size,
        epoch_num,
        grad_accu_steps,
        n_gpu,
        use_bert,
        multi_choice,
    )

    ep = 0
    acc = 0.00
    model_file = f"{model_type}-{model_prefix}-{ep}-{acc:.2f}.ckpt"

    if mode != "train":
        result_file = (
            f"results/{dataset}/{task}/{model_type}-{model_prefix}-{mode}.json"
        )
        vqa.predict(model_file, result_file)
        if not multi_choice:
            eval_oe.main(result_file, sample_list_path, mode)
        else:
            eval_mc.main(result_file, sample_list_path, mode)
    else:
        model_file = f"{model_type}-{model_prefix}-6-39.28.ckpt"
        vqa.run(model_file, pre_trained=False)


if __name__ == "__main__":
    torch.backends.cudnn.enabled = False
    torch.manual_seed(666)
    torch.cuda.manual_seed(666)
    torch.backends.cudnn.benchmark = True

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ngpu", dest="ngpu", type=int, default=0, help="number of gpus to use"
    )
    parser.add_argument(
        "--mode", dest="mode", type=str, default="train", help="[train, val, test]"
    )
    args = parser.parse_args()
    main(args)
