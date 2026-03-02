"use client";
import { useState, useEffect } from "react";
import Image from "next/image";
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { webApp, transcriptionApi } from "@/utils/api";
import { Manager } from "@/types/manager";
import { Specialist } from "@/types/specialist";

const CardLayout = () => {
  const [managers, setManagers] = useState<Manager[]>([]);
  const [selectedManager, setSelectedManager] = useState<Manager | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // Fetch managers data from webApp
  useEffect(() => {
    const fetchManagers = async () => {
      try {
        const response = await webApp.get("/managers-names");
        if (response.status === 200) {
          setManagers(response?.data?.detail?.managers);
        } else {
          console.error("Failed to fetch managers:", response.statusText);
        }
      } catch (error) {
        console.error("Error fetching managers:", error);
      }
    };
    fetchManagers();
  }, []);

  const handleManagerClick = async (managerName: string) => {
    setLoading(true);
    try {
      const response = await transcriptionApi.get(`/transcription-data?manager=${encodeURIComponent(managerName)}`);
      const managerData = response.data.result;
      
      if (managerData) {
        setSelectedManager({
          ...managerData,
          specialists: managerData.assistants.map((specialist: Specialist) => ({
            ...specialist,
            image: "/images/users/user-02.png",
          })),
        });
      }
    } catch (error) {
      console.error("Failed to fetch manager data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSpecialistClick = (specialistId: string) => {
    router.push(`/specialists/${specialistId}`);
  };

  const handleBackClick = () => {
    setSelectedManager(null);
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
      <div className="px-4 py-6 md:px-6 xl:px-7.5 flex justify-between items-center">
        <h4 className="text-xl font-semibold text-black dark:text-white">
          {selectedManager ? selectedManager.name : "Managers"}
        </h4>
        {selectedManager && (
          <button
            onClick={handleBackClick}
            className="text-sm bg-meta-4 text-white py-2 px-4 rounded hover:bg-red"
          >
            See all managers
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-2 p-4">
        {selectedManager
          ? selectedManager.specialists.map((specialist, key) => (
            <div
              key={key}
              className="flex flex-col items-center border border-stroke p-4 rounded-lg dark:border-strokedark dark:bg-boxdark hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => handleSpecialistClick(specialist.name)}
            >
              <Image
                src={specialist.image || "/images/users/user-02.png"}
                width={250}
                height={250}
                alt={specialist.name}
                className="rounded-full mb-4"
              />
              <h5 className="text-lg font-bold text-black dark:text-white">
                {specialist.name}
              </h5>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {specialist.role}
              </p>
            </div>
          ))
          : managers.map((manager, key) => (
            <div
              className="flex flex-col items-center border border-stroke p-4 rounded-lg dark:border-strokedark dark:bg-boxdark hover:shadow-lg transition-shadow cursor-pointer"
              key={key}
              onClick={() => handleManagerClick(manager.name)}
            >
              <Image
                src="/images/user/best-manager.png"
                width={250}
                height={250}
                alt={manager.name}
                className="rounded-full mb-4"
              />
              <h5 className="text-xl font-bold text-black dark:text-white mb-1 text-center">
                {manager.name}
              </h5>
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                {manager.role}
              </p>
            </div>
          ))}
      </div>
    </div>
  );
};

export default CardLayout;
