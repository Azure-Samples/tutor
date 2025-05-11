import { Profile } from "@/types/profile";
import { useState } from "react";

interface ProfileFormProps {
  profile: Profile;
  onChange: (profile: Profile) => void;
  readOnly?: boolean;
}

const ProfileForm: React.FC<ProfileFormProps> = ({ profile, onChange, readOnly }) => {
  const [localProfile, setLocalProfile] = useState<Profile>(profile);

  const handleChange = (field: keyof Profile, value: any) => {
    const updated = { ...localProfile, [field]: value };
    setLocalProfile(updated);
    onChange(updated);
  };

  return (
    <div className="flex flex-col items-center justify-start w-full max-w-2xl mx-auto bg-gray-100 dark:bg-gray-900 p-6">
      <div className="w-full bg-white shadow-default dark:bg-boxdark p-6 rounded-lg">
        <div className="flex flex-col gap-2">
          <input
            type="text"
            value={localProfile.name}
            onChange={e => handleChange("name", e.target.value)}
            className="input"
            placeholder="Name"
            disabled={readOnly}
          />
          <input
            type="text"
            value={localProfile.gender || ""}
            onChange={e => handleChange("gender", e.target.value)}
            className="input"
            placeholder="Gender"
            disabled={readOnly}
          />
          <input
            type="number"
            value={localProfile.age || ""}
            onChange={e => handleChange("age", parseInt(e.target.value))}
            className="input"
            placeholder="Age"
            disabled={readOnly}
          />
          <input
            type="text"
            value={localProfile.role}
            onChange={e => handleChange("role", e.target.value)}
            className="input"
            placeholder="Role"
            disabled={readOnly}
          />
          <input
            type="text"
            value={localProfile.level || ""}
            onChange={e => handleChange("level", e.target.value)}
            className="input"
            placeholder="Level"
            disabled={readOnly}
          />
          <textarea
            value={localProfile.details}
            onChange={e => handleChange("details", e.target.value)}
            className="input"
            placeholder="Details"
            disabled={readOnly}
          />
        </div>
      </div>
    </div>
  );
};

export default ProfileForm;
