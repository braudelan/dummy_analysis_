1. ### build the command for the specfic tool along with arguments
    - get a list of input files from command line
    - use regax to grab sample identifiers from input files and build output filenames with these identifiers
2. ### build the bsub command
    - get bsub arguments for options (e.g. `-queue`)
    - error and output log 
3. ### combine (1) and (2) to yield the complete command
    - remember to apply quotation marks on the tool command
4. ### run the complete command in shell
    - use the `subprocess` module
    