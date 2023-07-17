# YiVal

[![PyTest](https://github.com/YiVal/YiVal/actions/workflows/test.yml/badge.svg)](https://github.com/YiVal/YiVal/actions/workflows/pytest.yml)
[![Code style: yapf](https://img.shields.io/badge/code%20style-yapf-blue)](https://github.com/google/yapf)

## Introduction
YiVal is an innovative open-source project, rooted in the principles of the Yijing, focused on revolutionizing the end-to-end evaluation process of AI models. We aim to provide comprehensive insights into not only the individual components such as models and prompts but more importantly, the final output produced by their interaction.


## Key Features

**Effortless Integration:** YiVal offers simple wrappers for popular frameworks, including langchain. This means that integrating YiVal into your current projects is a straightforward process with minimal code changes.

**Easy Experimentation:** With YiVal, conducting experiments is a breeze. All you have to do is provide a driver using one of our templates. YiVal then manages the experiment, providing a comprehensive side-by-side comparison of different parameters, such as prompts.

**Comprehensive Evaluation:** YiVal is equipped to conduct both model-based and human evaluations. This provides a complete picture of your code's performance. Our unique edge lies in our capability to evaluate not just the quality, but also the cost of different code variations. This can significantly aid in optimization.

**Synthetic Test Set Generation:** YiVal can generate synthetic test sets as required, further streamlining your evaluation processes.

**Prompt Suggestions:** YiVal keeps up with the latest research and developments in AI and can provide prompt suggestions based on these, ensuring your models remain at the cutting edge.

**Results Tracking:** YiVal maintains a record of previous results, making it easy for you to identify and select the most suitable combination of parameters, prompts, and models for your specific needs.

**Efficient Comparison:** YiVal provides configurable settings for comparing top-k results. We also cache identical evaluations to save costs.

**Visibility Controls:** Choose between Eval mode and SxS mode. The latter allows you to hide answers when there are no differences, making the comparison process more efficient.

Certainly, here's a revised roadmap with each Hexagram having five action items and their corresponding Chinese characters:

Absolutely, here's the revised roadmap with support for multi-modal input types:

## Roadmap

Our roadmap for future features is inspired by the eight Hexagrams of the Yijing:

1. **Qian (The Creative, Heaven) 🌤️ (乾):** 
   - [ ] Support langchain prompts comparison
        - [ ] Support basic prompt with input variables from user input
        - [ ] Support prompt that has information from retrieval (e.g., database)
   - [ ] Implement a suggestion system for improving prompts
   - [ ] Support langchain model comparison
   - [ ] Support langchain memory comparison
   - [ ] Provide insights on cost and latency for different combinations
   - [ ] Develop a comprehensive user manual and tutorial

2. **Kun (The Receptive, Earth) 🌏 (坤):** 
   - [ ] Add support for multi-modal input types (e.g., audio, video, image) 
   - [ ] Implement multi-modal evaluation methods
   - [ ] Add auto-evaluation by the model(s) for multiple input types
   - [ ] Develop a system for importing and exporting evaluation data for multi-modal datasets
   - [ ] Enhance compatibility with more AI frameworks and libraries that support multi-modal data
   - [ ] Enable users to customize their multi-modal evaluation parameters

3. **Zhen (The Arousing, Thunder) ⚡ (震):** 
   - [ ] Implement novel AI evaluation metrics based on different use cases and input types
   - [ ] Develop a feature for real-time evaluation tracking
   - [ ] Create an alert system for significant metric changes
   - [ ] Provide a platform for researchers to share and discuss new metrics
   - [ ] Allow users to customize their evaluation metrics

4. **Xun (The Gentle, Wind) 🍃 (巽):** 
   - [ ] Improve user interface and navigation
   - [ ] Enhance the accessibility of the platform
   - [ ] Implement user-friendly error messages and troubleshooting guides
   - [ ] Optimize platform speed and efficiency
   
5. **Kan (The Abysmal, Water) 🌊 (坎):**
   - [ ] Develop automated debugging feature
   - [ ] Implement AI model failure prediction
   - [ ] Create a system for users to share and discuss debugging solutions
   - [ ] Allow users to report bugs and issues directly through the platform
   - [ ] Implement a feature for suggesting solutions to common issues

6. **Li (The Clinging, Fire) 🔥 (離):** 
   - [ ] Improve visualization of evaluation results
   - [ ] Develop a dashboard for tracking evaluation metrics
   - [ ] Allow users to customize their result visualization preferences
   - [ ] Implement a feature for sharing and exporting visualizations
   - [ ] Enable real-time updates in result visualizations

7. **Gen (Keeping Still, Mountain) 🏔️ (艮):** 
   - [ ] Develop robust error handling mechanisms
   - [ ] Improve version control
   - [ ] Implement a rollback feature for mitigating issues
   - [ ] Enhance security measures and data protection
   - [ ] Regularly update the platform to ensure stability and reliability

8. **Dui (The Joyous, Lake) 🏞️ (兌):** 
   - [ ] Collect user feedback and conduct user research
   - [ ] Implement UX enhancements based on user feedback and research
   - [ ] Regularly update the platform according to user needs and preferences
   - [ ] Develop a system for users to vote on potential new features
   - [ ] Maintain an active dialogue with the user community to foster engagement and satisfaction
   - [ ] Create a feature for users to share and discuss effective prompts
## Get Involved
We welcome contributions from the community to help us improve YiVal. Whether you're a developer looking to fix bugs or add features, or you're just passionate about AI and have great ideas, we'd love to hear from you. 

Please refer to our contribution guide for more information on how to get started.