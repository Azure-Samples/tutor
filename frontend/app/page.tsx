'use-client';
import Link from "next/link";
import Image from "next/image";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";

import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

export const metadata: Metadata = {
  title: "The Tutor",
  description: "Support for students in all dimensions.",
};

const functionalities = [
  {
    title: "Avatar",
    description: "Engage in interactive, real-world scenarios with your AI Avatar. Practice conversations, receive instant feedback, and build confidence for real-life situations.",
    href: "/avatar",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Chat",
    description: "Ask questions, discuss topics, and get clear, thoughtful explanations. The chat is your space for curiosity, support, and deeper understanding.",
    href: "/chat",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Essays",
    description: "Submit essays and receive detailed, constructive feedback. Improve your writing, argumentation, and critical thinking with every submission.",
    href: "/essays",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Questions",
    description: "Challenge yourself with quizzes and objective questions. Track your progress, identify strengths, and focus on areas for growth.",
    href: "/questions",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Configuration",
    description: "Personalize your learning environment. Adjust preferences and settings to create a study space that works for you.",
    href: "/configuration",
    icon: "/images/logo/logo.webp",
  },
];

const HomePage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb pageName="Welcome to The Tutor Learning Hub" subtitle="Serious learning, made engaging for all ages. Explore each feature below—every tool is designed to help you grow, master new skills, and enjoy the journey." />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {functionalities.map((func) => (
          <Link
            key={func.title}
            href={func.href}
            className="flex flex-col items-center p-8 bg-gradient-to-br from-blue-50 to-green-50 hover:from-cyan-100 hover:to-green-100 shadow-xl rounded-2xl transition-transform duration-200 cursor-pointer text-center border-2 border-cyan-200 hover:border-green-300 dark:bg-gradient-to-br dark:from-blue-900 dark:to-green-900 dark:hover:from-cyan-800 dark:hover:to-green-800 hover:scale-105"
          >
            <Image
              width={120}
              height={120}
              src={func.icon}
              alt={func.title}
              className="mb-4 rounded-full border-2 border-cyan-300 shadow bg-white"
            />
            <h3 className="text-xl font-extrabold text-blue-700 dark:text-cyan-200 mb-2">{func.title}</h3>
            <p className="mt-2 text-green-700 dark:text-green-100 text-base font-semibold">{func.description}</p>
          </Link>
        ))}
      </div>
    </DefaultLayout>
  );
};

export default HomePage;
