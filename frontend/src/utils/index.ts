

export function formatFileSize(sizeInBytes: number) {
    const units = ["B", "KB", "MB", "GB", "TB"];

    if (sizeInBytes === 0) return "0 B";

    let unitIndex = 0;
    while (sizeInBytes >= 1024 && unitIndex < units.length - 1) {
        sizeInBytes /= 1024;
        unitIndex++;
    }

    return `${sizeInBytes.toFixed(2)} ${units[unitIndex]}`;
}