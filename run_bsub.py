'''build the commands to run in Bsub'''
import re
import sys
import subprocess
import argparse

ENCODING = 'utf-8'

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-q', '--queue', type=str)
parser.add_argument('-m', '--memory', type=int)
parser.add_argument('-wd', '--working_dir', type=str, help='requested memory in ')
parser.add_argument('-c', '--command', dest='shell_command', type=str)
args = parser.parse_args()

## output of this command is a list of file names to iterate over
shell_command = args.shell_command

## bsub arguments
queue_command = f'-q {args.queue}'
memory =
memory_command = f'-m {args.memory}'
working_directory = args.working_dir

## run the initial shell command and grab the output
subprocess = subprocess.Popen([shell_command],
                        shell=True, stdout=subprocess.PIPE)
file_names = [byte.decode(ENCODING) for
              byte in subprocess.stdout.read().splitlines()]
# print(f'these are some of the file names'\
#       f'you asked for:\n{file_names[:10]}')


reg_expression = r'^\w+_\w+_\w+_R'
reg_compile = re.compile(reg_expression)

# with open('cutadapt_commands', 'w') as output_file:
    #todo functionalize the main for loop

for file_name in file_names:

    ## match the regax expression
    match = reg_compile.match(file_name)
    unique_sample_id = match.group()

    analysis_tool_command = f'cutadapt -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A'\
                            f'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT --times 2 -q 30'\
                            f'-m 20 -o 02_trimmed_reads/{unique_sample_id}_R1_trimmed.fastq'\
                            f'-p 02_trimmed_reads/{unique_sample_id}_R2_trimmed.fastq'\
                            f'01.fastq/{unique_sample_id}/_R1_001.fastq.gz'\
                            f'01.fastq\/{unique_sample_id}_R2_001.fastq.gz/'
    analysis_tool_command = f"'{analysis_tool_command}'"

    bsub_command = " ".join(
        [
            'bsub',
            queue_command,
            analysis_tool_command
        ]
    )

    print(bsub_command)







