from langkit.core.workflow import EvaluationWorkflow
from langkit.metrics.library import lib
import nltk
from nltk.downloader import Downloader

downloader = Downloader()
print(downloader.is_installed('vader_lexicon'))
print(downloader.is_installed('vader_lexicon'))
print(downloader.is_installed('vader_lexicon'))

wf = EvaluationWorkflow([lib.all_metrics()])
wf.init()


