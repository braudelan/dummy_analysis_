import pdb
import pysam
import os
import subprocess

#
# def join_n_split(*args: str, is_text=True, stdout=None):
#     """helper function to join multiple commands and pass them to subprocess.run()"""
#     joined = " ".join([*args])
#     split = joined.split()
#     return split

# screen by size and convert to bam
def sam_to_bam(bsub_options, sam_file_name, size):

    input_sam = sam_file_name + '.sam'
    temp_sam_path = sam_file_name + '_temp.sam'
    temp_bam_path = sam_file_name + '_temp.bam'
    bam_path = sam_file_name + '.bam'

    # --------------------------- exclude umapped, discordant or small reads ------
    # write the header
    write_header = fr'samtools view -H {input_sam}'
    with open(temp_sam_path, 'w+') as temp_sam:
        p0 = subprocess.run(write_header.split(), stdout=temp_sam, text=True)
    # pdb.set_trace()

    # exclude unmapped and discordant reads (no header)
    view_no_unmapped_or_discordant = fr'samtools view -F 4 -f 0x2 {input_sam}'
    p1 = subprocess.run(view_no_unmapped_or_discordant.split(), capture_output=True, text=True)

    # exclude alignments shorter than <size> and append to temp sam file
    print_by_size = fr"awk -F '\t' '{{if ($9> {size}) print $_;}}'"  # print out reads longer than <size>
    with open(temp_sam_path, 'a+') as temp_sam:
        p2 = subprocess.run(['awk', '-F', r'\t', f'{{if ($9> {size}) print $_;}}'],
                                                    input=p1.stdout, stdout=temp_sam, text=True)
        print(p2.args)
    # --------------------------- convert to bam, sort and create index file ------
    # convert temp sam file to bam
    view_as_bam = fr"samtools view -b {temp_sam_path}"
    with open(temp_bam_path, 'w+') as temp_bam:
        subprocess.run(view_as_bam.split(), stdout=temp_bam, text=True)

    # create an output bam file; sort temp bam file by coordinate and send sorted output to output bam file
    with open(bam_path, 'w+') as bam_file:
        pysam.sort('-o', bam_path, temp_bam_path)

    # create index file for random access
    pysam.index(bam_path)

    # remove temp files
    os.remove(temp_sam_path)
    os.remove(temp_bam_path)


# if __name__ == 'main':
#     sam_to_bam('test', 120)

# with open(sam_path, 'r') as open_sam,\
#      open(temp_bam_path, 'w')  as open_temp_bam:
#
#     sam_file = pysam.AlignmentFile(open_sam, 'r')
#     bam_temp_file = pysam.AlignmentFile(open_temp_bam,
#                                         'wb', template=sam_file)
#
#     # size selection
#     for alignment in sam_file:
#         length = alignment.query_length
#         if length > size:
#             bam_temp_file.write(alignment)
