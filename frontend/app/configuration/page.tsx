import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";

export const metadata: Metadata = {
  title: "Tutor | Configuration",
  description: "This is the Transcription configuration page for Tutor.",
};

const configOptions = [
  {
    title: "Cases",
    description: "Manage and configure real-world cases for students to practice and be evaluated on. Perfect for scenario-based learning and oral exams.",
    href: "/configuration/cases",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Themes",
    description: "Create, edit, and organize themes for essay and argumentation practice. Guide students to develop critical thinking and structured responses.",
    href: "/configuration/themes",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Questions",
    description: "Design and manage objective questions for quizzes and assessments. Track student progress and ensure comprehensive evaluation.",
    href: "/configuration/questions",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Agents",
    description: "Create and manage AI agent assemblies that power essay and question evaluation workflows. Configure deployments, temperature, and instructions.",
    href: "/configuration/agents",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Upskilling",
    description: "Evaluate teaching plans with agentic coaching feedback. Analyze paragraph structure and pedagogical effectiveness.",
    href: "/configuration/upskilling",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "Evaluation",
    description: "Run agent quality checks by creating datasets and executing evaluation runs against deployed agents.",
    href: "/configuration/evaluation",
    icon: "/images/logo/logo.webp",
  },
  {
    title: "LMS Gateway",
    description: "Trigger and inspect LMS synchronization jobs. Connect to Moodle or Canvas and schedule recurring syncs.",
    href: "/configuration/lms-gateway",
    icon: "/images/logo/logo.webp",
  },
];

const ConfigurationPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb pageName="Configuration & Management" subtitle="Organize, evaluate, and empower student learning. Choose a tool below to get started!" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {configOptions.map((opt) => (
          <Link
            key={opt.title}
            href={opt.href}
            aria-label={`Open ${opt.title} configuration`}
            className="flex min-h-56 flex-col items-center p-8 bg-gradient-to-br from-blue-50 to-green-50 hover:from-cyan-100 hover:to-yellow-100 shadow-xl rounded-2xl transition-transform duration-200 cursor-pointer text-center border-2 border-cyan-200 hover:border-green-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2 dark:bg-gradient-to-br dark:from-blue-900 dark:to-green-900 dark:hover:from-cyan-800 dark:hover:to-green-800 hover:scale-105 group"
          >
            <Image
              width={100}
              height={100}
              src={opt.icon}
              alt={`${opt.title} configuration`}
              className="mb-4 rounded-full border-2 border-cyan-300 shadow bg-white group-hover:scale-110 group-hover:rotate-6 transition-transform duration-300"
            />
            <h3 className="text-lg font-bold text-blue-700 dark:text-cyan-200 mb-2 group-hover:text-green-700 transition-colors duration-300">{opt.title}</h3>
            <p className="mt-2 text-green-700 dark:text-green-100 text-base font-medium group-hover:text-yellow-700 transition-colors duration-300">{opt.description}</p>
          </Link>
        ))}
      </div>
    </DefaultLayout>
  );
};

export default ConfigurationPage;
