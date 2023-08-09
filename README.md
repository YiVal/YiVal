# YiVal

[![PyTest](https://github.com/YiVal/YiVal/actions/workflows/test.yml/badge.svg)](https://github.com/YiVal/YiVal/actions/workflows/pytest.yml)
[![Code style: yapf](https://img.shields.io/badge/code%20style-yapf-blue)](https://github.com/google/yapf)

<details open="open">
<summary>Table of Contents</summary>

- [About](#about)

</details>

---

## About

YiVal is an adaptable AI development framework, designed to provide a tailored experimentation experience. Whether you're a hands-on developer or leaning into automation, YiVal is equipped for both:

- **Data Input**: Choose between manual data input or let the framework handle auto-generation.
- **Variations**: Manually set parameter and prompt variations or utilize the automated capabilities for optimal settings.
- **Evaluation**: Engage with manual evaluators or leverage the built-in automated evaluators for efficient results.

On the horizon is the YiVal Agent, an ambitious addition aimed at autonomously driving the entire experimentation process. With its blend of manual and automated features, YiVal stands as a comprehensive solution for AI experimentation, ensuring flexibility and efficiency every step of the way.

<details>
<summary>Screenshots</summary>
<br>

### Best Parameter Combination
![Screenshot 2023-08-08 at 9 21 36 PM](https://github.com/YiVal/YiVal/assets/1544154/6af77f6f-a693-4781-8a75-e36ccdd24624)

### Data Analysis
![Screenshot 2023-08-08 at 9 25 14 PM](https://github.com/YiVal/YiVal/assets/1544154/b4f17e5c-353f-465e-8198-a1374a03857d)


### Test Cases Side by Side
![Screenshot 2023-08-08 at 9 25 20 PM](https://github.com/YiVal/YiVal/assets/1544154/1d7cbd06-b9c6-4a98-9498-a52a13d1d805)


</details>

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
