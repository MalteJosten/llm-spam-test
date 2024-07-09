# Pipeline for Testing Spam Filter's Effectiveness against LLM-modified Spam Mails
This testing pipeline is part of the paper *Investigating the Effectiveness of Bayesian Spam Filters in Detecting LLM-modified Spam Mails*.
It helps to measure the effectiveness and robustness of spam filters (we tested against an instance of SpamAssassin) in detecting spam mails that have been modified using a large language model (LLM).

In this setup, we deployed a [Mailpit mailserver](https://hub.docker.com/r/axllent/mailpit) that uses [SpamAssassin](https://hub.docker.com/r/axllent/spamassassin) to label emails in the inbox as either spam or ham.

## Executing the Testing Pipeline
The initial step for this pipeline should be to navigate into `scripts`, create a python virtual environment with
```
python -m venv venv
```
and activate it with
```
source venv/bin/activate
```
You may want to change some venv settings. Use the [official documentation](https://docs.python.org/3/library/venv.html) for more details.

Additionally, you might want to install the required pip packages with
```
pip install -r requirements.txt
```

After configuring the individual scripts (`stack_pre_process.sh`, `stack_groundtruth.sh`, `stack_dict_test.sh`, and `stack_llm_test.sh`), you can execute the entire pipeline with
```
./stack_execute_all.sh
```
See the individual steps below for a description of each script.

### 1. Pre-process data set
1. Copy all spam emails into `data/mails/raw`. It is also possible to put them into subfolders.
2. Navigate into `scripts/`, and, after specifying the `RAW_DIRS` variable (should list all directories that contain spam emails) in the bash script `stack_pre_process.sh`, execute it with

```
./stack_pre_process.sh
```
This will
- convert all files found in the directories given in `RAW_DIRS` to .eml files and copy them into `data/mails/spam-in`
- anonymize email addresses given in the SMTP header fields Bcc, Cc, From, and To
- create two data sets (in `data/mails/spam-mod`): *original* and *minimal*

### 2. Generate ground truth
Set `MAILPIT_URI` in `stack_groundtruth.sh` to your mailserver's IP address and execute the script with
```
./stack_groundtruth.sh
```
This will
- send the mails contained in (the subdirectories of) `data/mails/spam-mod/<dataset-name>` to the mailserver
- retrieve their spam classification labels
- create a summary for both datasets, *original* and *minimal* at `results/sum_orig_<dataset-name>.json`
- create the groundtruth for each dataset at `results/gt_<dataset-name>.json` and an overarching groundtruth that comprises both groundtruths at `results/GT.json`

### 2. Run dictionary test
With the script `stack_dict_test.sh`, we use a dictionary generated from a [list of spam-like words](https://mailmeteor.com/blog/spam-words) to replace words and formulations that might have a negative influence on the spam classification.<br>
Again, the mailserver's IP address (`MAILPIT_URI`) has to be set before executing the script with
```
./stack_dict_test.sh
```
This will
- modify email bodies by replacing spam-like words with the help of the dictionary (`data/dictionary/meteor_dict.json`)
- merge the modified email bodies with SMTP headers, and save them at `data/dictionary/mails`
- send the modified emails to the mail server
- retrieve the spam classification labels
- create a test summary, and save it at `results/sum_mod_dict_<dataset-name>.json`

The test summary includes information about the spam filter's effectiveness against the dictionary-modified spam emails.

### 3. Run LLM-modified test
```
./stack_llm_test.sh
```
- send the email bodies contained in the ground truth (`results/GT.json`) to the OpenAI API to request and retrieve their modified version
- merge modified email bodies with SMTP headers, and save them at `data/gpt/mails`
- send the modified emails to the mail server
- retrieve the spam classification labels
- create a test summary, and save it at `results/sum_mod_gpt_<dataset-name>.json`

The test summary includes information about the spam filter's effectiveness against the LLM-modified spam emails.

## Citation and Attribution
<--
If you use (parts) of our pipeline, please cite our work as follows:
```

```
-->

In case of questions or other inquiries, please contact Malte Josten ([malte.josten@uni-due.de](mailto:malte.josten@uni-due.de)).
