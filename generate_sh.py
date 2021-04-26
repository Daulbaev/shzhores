import argparse

'''
Generates .sh file to run using sbatch
Example usage: python3 generate_sh.py -a dataset lr optimizer n
'''

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Zhores sh generator')
    parser.add_argument(
        "-a",
        "--arguments",
        nargs="+",
        help="Arguments separated by space, e.g., 'dataset lr optimizer'",
    )
    parser.add_argument("--job_name", type=str, default="train")
    parser.add_argument("-c", type=int, default=4)
    parser.add_argument("-N", type=int, default=1)
    parser.add_argument("--gpus", type=int, default=1)
    parser.add_argument(
        "-m",
        "--modules",
        nargs="+",
        default=["compilers/gcc-5.5.0", "gpu/cuda-10.2", "python/pytorch-1.5.0"],
        help="Arguments separated by space, e.g., 'compilers/gcc-5.5.0 gpu/cuda-10.2 python/pytorch-1.5.0'",
    )
    parser.add_argument("--wandb_hash", default=None)
    parser.add_argument("--script_name", type=str, default="train.py")
    args = parser.parse_args()
    print(args.arguments)

    s = f"""#!/bin/bash
#SBATCH -N {args.N}
#SBATCH --job-name {args.job_name}
#SBATCH -c {args.c}
#SBATCH --gpus {args.gpus}

for i in "$@"
do
case $i in
"""
    for a in args.arguments:
        if len(a) == 1:
            hyp = '-'
        else:
            hyp = '--'
        s += f'''    {hyp}{a}=*)\n    {a}="${{i#*=}}"\n    shift\n    ;;\n'''
    s += '''    *)
        echo ERROR! WRONG ARGUMENTS!
        exit 1
    ;;
esac
done\n\n'''

    for module in args.modules:
        s += f"module load {module}\n"
    if args.wandb_hash is not None:
        s += f"wandb login {args.wandb_hash}\n\n"
    s_call = f"python3 {args.script_name} "
    for a in args.arguments:
        if len(a) == 1:
            hyp = '-'
        else:
            hyp = '--'
        s_call += f"{hyp}{a} ${a} "
    s += s_call + "\n"

    s_example = f"sbatch -p gpu YOUR_SCRIPT_NAME.sh "
    for a in args.arguments:
        if len(a) == 1:
            hyp = '-'
        else:
            hyp = '--'
        s_example += f"{hyp}{a} {a} "
    s += f"""'
    Example:
    
    {s_example}
:'"""
    print(s)




