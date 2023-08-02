# YiVal

[![PyTest](https://github.com/YiVal/YiVal/actions/workflows/test.yml/badge.svg)](https://github.com/YiVal/YiVal/actions/workflows/pytest.yml)
[![Code style: yapf](https://img.shields.io/badge/code%20style-yapf-blue)](https://github.com/google/yapf)

## Introduction

YiVal is an innovative open-source project,
rooted in the principles of the Yijing,
focused on revolutionizing the end-to-end evaluation process of AI models.
We aim to provide comprehensive insights into not only the individual components
such as models and prompts but more importantly,
the final output produced by their interaction.

## Using Yival for auto prompt generation
![2023-08-02 00 01 32](https://github.com/YiVal/YiVal/assets/1544154/116e2387-dc41-4d13-b25d-79e55f25bb71)


## Result SxS

![SxS](https://github.com/YiVal/YiVal/assets/1544154/c667a749-8bdc-469e-a2d2-5086f7bac73e)

## Roadmap

**Qian** (The Creative, Heaven) 🌤️ (乾):

- [x] Setup the framework for wrappers that can be used directly
    in the production code.
    - [x] Set up the BaseWrapper
    - [x] Set up the StringWrapper
- [x] Setup the config framework
- [x] Setup the experiment main function
- [x] Setup the evaluator framework to do evaluations
    - [x] One auto-evaluator
    - [x] Ground truth matching
    - [ ] Human evaluator
- [x] Interactive evaluator
- [x] Reader framework that be able to process different data
    - [ ] One reader from csv
- [x] Output parser - Capture detailed information
- [ ] Documents
- [ ] Git setup
- [ ] Cotribution guide
- [x] End2End Examples
- [ ] Release
