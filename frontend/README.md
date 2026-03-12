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
- **Configuration:** Personalize your learning environment and manage settings, including question administration pages for graders and answers.

## Questions Administration Pages

The configuration area now includes dedicated routes for question-evaluation entities:

- `/configuration/questions/graders` — Manage grader definitions (`agent_id`, `dimension`, `deployment`)
- `/configuration/questions/answers` — Manage answer records used in question evaluation flows

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
   - Edit `.env.local` with APIM gateway URL.
   - Required key: `NEXT_PUBLIC_APIM_BASE_URL`.
   - The frontend routes all backend traffic through APIM paths: `/api/avatar`, `/api/essays`, `/api/questions`, `/api/configuration`, `/api/upskilling`, `/api/chat`, `/api/evaluation`, `/api/lms-gateway`.
   - Avatar speech credentials are brokered by the avatar backend and do not require public speech keys in the frontend build.
   - In production, always use `https://` APIM gateway URLs.

## Deploying to Azure

- The frontend is designed to be deployed as an Azure Static Web App.
- Use the Azure portal or CLI to link your GitHub repository and set build settings.
- The infrastructure Bicep files in `/infra` will provision the required Azure resources.

For more details, see the main project README and Azure Static Web Apps documentation.
