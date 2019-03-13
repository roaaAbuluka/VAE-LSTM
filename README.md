## A Generative Deep Generative Framework for Paraphrase Generation
This is my ongoing implementation of the paper by Gupta et al.

## Data
MSCOCO, PPDB, Wikianswers are available in this [repo](https://github.com/iamaaditya/neural-paraphrase-generation/tree/dev)
I put source / target files into one file with the follwing command.
```
paste train_source.txt train_target.txt > train.txt
paste test_source.txt test_target.txt > test.txt
```
