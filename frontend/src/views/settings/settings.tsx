import React, { useEffect, useState } from "react";
import { GloblaFile } from "./components/tabFiles";
// import { General } from "./components/tabGeneral";
import { TabUsers } from "./components/tabUsers";
import { TabStorge } from "./components/tabStorage";
import { TabFilesManagement } from "./components/tabFilesManagement";
import { useAuth } from "@/components/authProvider";
import { TiCloudStorage } from "react-icons/ti";
import { Role } from "@/enums/enums";
import { FiUsers } from "react-icons/fi";
import { LuFiles } from "react-icons/lu";
import { useSearchParams } from "react-router-dom";

interface SettingsViewProps {}

interface TabItem {
  label: string;
  value: string;
  icon: React.ReactNode | null;
  menu: React.ReactNode;
  roles: Role[];
}

const allTabs: TabItem[] = [
  {
    label: "Пользователи",
    value: "users",
    icon: <FiUsers size={18} />,
    menu: <TabUsers />,
    roles: [Role.ADMIN],
  },
  {
    label: "Хранилище",
    value: "storage",
    icon: <TiCloudStorage size={18} />,
    menu: <TabStorge />,
    roles: [Role.ADMIN],
  },
  {
    label: "Файлы",
    value: "files",
    icon: <LuFiles size={18} />,
    menu: <TabFilesManagement />,
    roles: [Role.ADMIN],
  },
];

const SettingsView: React.FC<SettingsViewProps> = ({}) => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState("storage");
  const [activeTabContent, setActiveTabContent] = useState<React.ReactNode>(
    <GloblaFile />,
  );
  // const [activeTabContent, setActiveTabContent] = useState<React.ReactNode>(<General />);
  const [filteredTabs, setFilteredTabs] = useState<TabItem[]>([]);

  useEffect(() => {
    // Get initial tab from URL params if it exists
    const tabParam = searchParams.get("tab");
    const initialTab =
      tabParam && allTabs.some((tab) => tab.value === tabParam)
        ? tabParam
        : "storage";

    setActiveTab(initialTab);
  }, []);

  useEffect(() => {
    // Filter tabs based on user role
    const tabs = allTabs.filter(
      (tab) => user?.role && tab.roles.includes(user.role),
    );
    setFilteredTabs(tabs);

    // Ensure the active tab is valid for the user's role
    const isValidTab = tabs.some((tab) => tab.value === activeTab);
    if (!isValidTab && tabs.length > 0) {
      const newActiveTab = tabs[0].value;
      setActiveTab(newActiveTab);
      setActiveTabContent(tabs[0].menu);
      // Update URL param when tab is reset due to role change
      setSearchParams({ tab: newActiveTab });
    }
  }, [user?.role, activeTab]);

  useEffect(() => {
    const newContent = filteredTabs.find(
      (tab) => tab.value === activeTab,
    )?.menu;
    if (newContent) {
      setActiveTabContent(newContent);
    }
  }, [activeTab, filteredTabs]);

  const handleTabChange = (tabValue: string) => {
    setActiveTab(tabValue);
    // Update URL search param when tab changes
    setSearchParams({ tab: tabValue });
  };

  return (
    <main className="">
      <h1 className="text-2xl font-semibold py-4">Настройки</h1>
      <div className="">
        <div
          className={`bg-muted text-muted-foreground p-1 rounded-md flex text-sm`}
        >
          {filteredTabs.map((item) => {
            return (
              <button
                key={item.value}
                className={`flex-1 flex items-center justify-center gap-1.5 rounded-md py-1.5 px-3 font-semibold ${activeTab == item.value ? "bg-background shadow-sm text-black" : null} hover:cursor-pointer`}
                onClick={() => handleTabChange(item.value)}
              >
                {item.icon && item.icon}
                {item.label}
              </button>
            );
          })}
        </div>
        <div className="mt-4">{activeTabContent}</div>
      </div>
    </main>
  );
};

export default SettingsView;
