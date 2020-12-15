"""
Run a series of jobs with a specified analysis tool.

    This script grabs a list of files from a given directory (input_dir)
and feeds each file into the command of a specified analysis tool.
the analysis tool command is then wrapped with the bsub command.
    both the input_dir, the analysis tool arguments and the bsub arguments can
be provided by the user as arguments of the main script.

    Todo:
        * write the main loop as a function.
        * provide a defualt -oe parmeter for bsub
        * make sure no email is sent after job completion if error and output are saved to file.
"""

import os
import re
import subprocess
import argparse
import hashlib
from datetime import datetime

ENCODING = 'utf-8'

# parse command line arguments
parser = argparse.ArgumentParser()

# argumetns for the job to be run
parser.add_argument('-in', '--input_dir',
                    help='directory to look for files to be processed')
parser.add_argument('-out', '--output_dir',
                    help='directory where processed files are saved' )
parser.add_argument('-regax',
                    help='the regax expression to be substituted into the command')
parser.add_argument('-c', '-command',
                    help='the command to be executed by bsub')
# bsub arguments
parser.add_argument('-q', '--queue', type=str)
parser.add_argument('-m', '--memory', type=int, help='requested memory in MB')

args = parser.parse_args()

## bsub options
queue = ['-q', args.queue]
required_memory = f'rusage[mem={args.memory}MB]'
memory = ['-R', required_memory] if args.memory else None

# job specific variables
input_dir = args.input_dir
output_dir = args.output_dir
regax_expression = args.regax
job_command = args.command

# get file names
get_file_names = subprocess.Popen([f'ls -1 {input_dir}'],
                                  shell=True, stdout=subprocess.PIPE)
file_names = [byte.decode(ENCODING) for
              byte in get_file_names.stdout.read().splitlines()]

## run a busb job for every file
reg_expression = r'^\w+_\w+_\w+_R'
reg_compile = re.compile(reg_expression)
for file_name in file_names:

    ## match the regax expression
    match = reg_compile.match(file_name)
    unique_sample_id = match.group()

    # generate a job hash
    now = datetime.now()
    job_and_time = f'{unique_sample_id}.{now}'.encode()
    job_hash = hashlib.md5(job_and_time).hexdigest()

    # job file name
    job_id = f'job.{job_hash}'


    # build the command for the specific tool in use\
    # using the unique sample ID
    analysis_tool_command = f'cutadapt -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A '\
                            f'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT --times 2 -q 30 '\
                            f'-m 20 -o 02_trimmed_reads/{unique_sample_id}1_trimmed.fastq '\
                            f'-p 02_trimmed_reads/{unique_sample_id}2_trimmed.fastq '\
                            f'01.fastq/{unique_sample_id}1_001.fastq.gz '\
                            f'01.fastq/{unique_sample_id}2_001.fastq.gz/'
    analysis_tool_command = f"'{analysis_tool_command}'"

    # build the paths and commands for bsub's output\
    # and error files
    error_file_command = ['-e', f'err/{job_id}']
    output_file_command = ['-o',f'out/{job_id}']

    commands = [
        'bsub',
        queue,
        memory,
    #     error_file_command,
    #    output_file_command,
        analysis_tool_command,
    ]

    commands_to_run = []
    for command in commands:
        if command and type(command) != list:
            commands_to_run.append(command)
        elif command and type(command) == list:
            commands_to_run.extend(command)
        else:
            continue

    # run the complete command in bash		
    # command_to_run = " ".join(commands_to_run)
    # subprocess.run(command_to_run, text=True, shell=True)







