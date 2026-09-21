# Agentic Mutational Signature Pipeline

Agentic Python pipeline for mutational signature analysis with
data QC, preprocessing, model selection, and human-in-the-loop decisions.

## Execution Design

The pipeline is designed to run with the same scientific workflow on either:

- a local computer
- a remote server or HPC cluster

The pipeline first inspects the input data and records:

- data type
- data location
- dataset size
- number of files/samples/features
- estimated computational requirements

An execution planner then selects the appropriate backend:

- LocalExecutor
- Server/SLURM Executor

The scientific analysis code remains the same regardless of execution location.