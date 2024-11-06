# The Tutor Application

"The Tutor" is an intelligent tutoring platform designed to provide students with personalized educational support through interactive AI-driven experiences. The platform leverages both text-based and avatar-based interactions to engage students, offering a wide variety of learning aids such as real-time question answering, essay evaluation, and interactive conversation. By integrating advanced large, visual and multimodal language models, "The Tutor" helps students improve their learning outcomes while providing teachers with insightful evaluation tools.

## Core Architecture and Components

![Core Architecture](./.assets/architecture.png)

This project framework provides the following components:

### Avatar and Textual Interaction Layers

Students can engage with the platform through two main interfaces: the Avatar Interaction and the Textual (Async) Interaction. The Avatar Interaction offers a more immersive learning experience, providing real-time conversational feedback through an AI avatar that uses a Speech Avatar Engine to synthesize speech. In parallel, the Textual Interaction allows for more asynchronous interaction, where students can receive detailed responses in text form. Both interaction methods are processed by their respective engines, the Avatar Engine and Textual Engine, which ensure a smooth and context-aware experience by leveraging Azure OpenAI and cognitive services.

### AI Engine and Vector Database

The heart of "The Tutor" is its AI Engine (powered by Azure OpenAI), which processes interactions and provides intelligent responses based on student input. The platform stores interaction data and semantic representations in a Vector Database (Azure AI Search), allowing the AI engine to reference past conversations and retrieve relevant information for current interactions, enhancing the overall learning experience through personalization and memory retention.

### Question and Essay Evaluation Systems

"The Tutor" features two key learning modules: the Questions Engine and the Essay Engine, which allow students to submit questions and essays for automatic evaluation. The Question Interface supports instant query submissions, while the Essay Interface enables students to submit detailed essays for evaluation. Both engines are supported by machine learning models that evaluate the students' input and provide feedback.

### Evaluation Models and Professor Dashboard

The evaluation of student responses is carried out by the Evaluation Model, which runs AI-based assessments on both essays and questions. The evaluation results are then made available on the Professor Dashboard, where educators can monitor student performance, adjust configurations via the Configure API, and review detailed student progress logs. The dashboard also provides access to the Evaluation History, where professors can review the historical progress of students' submissions and the AI's assessments.

### Conversation and Memory Management

An essential feature of "The Tutor" is its Conversation History module, which stores previous interactions to maintain continuity in conversations. The Avatar Questions Memory ensures that the AI avatar can recall and build upon previous queries posed by the student, providing a coherent and personalized learning journey. The Conversation Preprocessor also uses natural language processing to enhance the quality and relevance of the conversation before passing it to the AI engine for response generation.

## Business Goals and Use Cases

The Tutor might be applied on different scenarios.

- Personalized Learning Experience

"The Tutor" aims to enhance student learning by offering individualized feedback, allowing each student to learn at their own pace with personalized interactions.

- Automated Student Evaluations

The platform provides automated assessment tools for essays and questions, freeing up valuable time for educators while maintaining high standards for feedback quality.

- Scalability and Adaptability

Designed with scalability in mind, "The Tutor" can handle increasing volumes of student interactions without compromising the quality of service, thanks to its use of Azure services and AI-driven models.

- Teacher Support and Insights

Through the Professor Dashboard, educators are provided with real-time insights into student progress, enabling them to tailor lesson plans and interventions based on objective data.

- Continuous Learning and Memory

By using conversation history and memory, "The Tutor" ensures continuity in the learning process, helping students build upon previous sessions and facilitating long-term retention of knowledge.

## Getting Started

### Prerequisites

(ideally very short, if any)

- OS
- Library version
- ...

### Installation

(ideally very short)

- npm install [package name]
- mvn install
- ...

### Quickstart
(Add steps to get up and running quickly)

1. git clone [repository clone url]
2. cd [repository name]
3. ...


## Demo

A demo app is included to show how to use the project.

To run the demo, follow these steps:

(Add steps to start up the demo)

1.
2.
3.

## Resources

(Any additional resources or related projects)

- Link to supporting information
- Link to similar sample\
- ...