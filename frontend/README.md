# Tutor Frontend (Next.js)

This is the frontend for The Tutor platform, built with [Next.js](https://nextjs.org/). It provides a modern, interactive web interface for students and educators to access all features of the Tutor system.

## Objective

The frontend enables:

- Student and teacher login (if enabled)
- Access to all learning modules: Avatar, Chat, Essays, Questions, and Configuration
- Real-time and asynchronous AI-powered feedback
- Submission and review of essays and questions
- Visualization of evaluation history and progress

## Main Functionalities

- **Avatar:** Practice conversations with an AI avatar, including speech synthesis and real-time feedback.
- **Chat:** Ask questions and discuss topics with the AI.
- **Essays:** Submit essays for detailed, multi-agent evaluation.
- **Questions:** Answer objective questions and receive instant, multi-part feedback.
- **Configuration:** Personalize your learning environment and manage settings.

## Infrastructure Requirements

- Node.js 18+
- Access to the Tutor backend APIs (see main README)
- (For production) Azure Static Web Apps or compatible static hosting

## Running Locally

1. Install dependencies:

   ```pwsh
   npm install
   # or
   yarn install
   ```

2. Start the development server:

   ```pwsh
   npm run dev
   # or
   yarn dev
   ```

   The app will be available at [http://localhost:3000](http://localhost:3000).

3. Configure API endpoints:
   - Edit `.env.local` or `process.env` to point to your backend API URLs.

## Deploying to Azure

- The frontend is designed to be deployed as an Azure Static Web App.
- Use the Azure portal or CLI to link your GitHub repository and set build settings.
- The infrastructure Bicep files in `/infra` will provision the required Azure resources.

For more details, see the main project README and Azure Static Web Apps documentation.
