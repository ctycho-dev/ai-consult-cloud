import React, { useState, useEffect } from "react";
import { Select, Textarea, Button } from '@mantine/core';
import { toast } from 'sonner'
import {
    useGetSettingsQuery,
    useCreateSettingsMutation
} from "@/api/settings";


interface GeneralProps { }

const models = [
    { value: 'default', label: 'По умолчанию' },
    { value: 'gpt4', label: 'Chat GPT 4' }
]


export const General: React.FC<GeneralProps> = ({ }) => {
    const [selectedModel, setSelectedModel] = useState<string | null>(null);
    const [promptValue, setPromptValue] = useState('');
    const [loading, setLoading] = useState(false);
    const { data: settings } = useGetSettingsQuery();
    const [createSettings] = useCreateSettingsMutation();

    useEffect(() => {
        if (settings) {
            setSelectedModel(settings.model || models[0].value);
            setPromptValue(settings.prompt || '');
        }
    }, [settings]);


    const handleSaveSettings = async () => {
        setLoading(true);

        try {
            if (selectedModel) {
                await createSettings({ model: selectedModel, prompt: promptValue }).unwrap();
                close()
                toast.success('Настройки обновлены')
            }
        } catch (error) {
            toast.error(`Failed to save settings: ${error}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="border border-border rounded-md bg-card p-4">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Общие настройки</h2>
                <Button justify="end" variant="filled" color="green" onClick={handleSaveSettings} loading={loading} loaderProps={{ type: 'dots' }}>Сохранить изменения</Button>
            </div>
            <div>
                <Select
                    mb={16}
                    label="Модель"
                    placeholder="Pick value"
                    data={models}
                    value={selectedModel}
                    onChange={setSelectedModel}
                />
                <Textarea
                    label="Prompt"
                    placeholder="Введите данные"
                    value={promptValue}
                    onChange={(event) => setPromptValue(event.currentTarget.value)}
                />
            </div>
        </div>
    )
}