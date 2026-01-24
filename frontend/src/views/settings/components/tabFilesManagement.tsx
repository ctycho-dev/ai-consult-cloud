import React, { useState, useEffect, useMemo } from "react";
import { useLazyGetFilePageQuery } from "@/api/file";
import { useGetStoragesQuery } from "@/api/storage";
import { FileState } from "@/enums/enums";
import { IFile } from "@/interfaces/file";
import { IStorage } from "@/interfaces/storage";
import {
  Table,
  Pagination,
  TextInput,
  Select,
  Badge,
  Group,
  Stack,
  Text,
  Loader,
  Tooltip
} from "@mantine/core";
import { IconSearch, IconFilter } from "@tabler/icons-react";
import { format } from "date-fns";

interface TabFilesManagementProps { }

const FILE_STATUS_COLORS: Record<FileState, string> = {
  [FileState.PENDING]: "gray",
  [FileState.UPLOADING]: "blue",
  [FileState.STORED]: "cyan",
  [FileState.INDEXING]: "yellow",
  [FileState.INDEXED]: "green",
  [FileState.DELETING]: "orange",
  [FileState.UPLOAD_FAILED]: "red",
  [FileState.DELETE_FAILED]: "red",
};

const TIME_FILTER_OPTIONS = [
  { value: "all", label: "Все время" },
  { value: "24h", label: "Последние 24 часа" },
  { value: "48h", label: "Последние 48 часов" },
  { value: "7d", label: "Последняя неделя" },
  { value: "30d", label: "Последний месяц" },
];

const STATUS_OPTIONS = [
  { value: "all", label: "Все статусы" },
  { value: FileState.PENDING, label: "Ожидание" },
  { value: FileState.UPLOADING, label: "Загрузка" },
  { value: FileState.STORED, label: "Сохранено" },
  { value: FileState.INDEXING, label: "Индексация" },
  { value: FileState.INDEXED, label: "Индексировано" },
  { value: FileState.DELETING, label: "Удаление" },
  { value: FileState.UPLOAD_FAILED, label: "Ошибка загрузки" },
  { value: FileState.DELETE_FAILED, label: "Ошибка удаления" },
];

export const TabFilesManagement: React.FC<TabFilesManagementProps> = () => {
  const ITEMS_PER_PAGE = 20;

  // State
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [selectedStorage, setSelectedStorage] = useState<string>("all");
  const [selectedTimeFilter, setSelectedTimeFilter] = useState<string>("all");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // API hooks
  const [triggerQuery, { data: filesData, isLoading, isFetching }] =
    useLazyGetFilePageQuery();
  const { data: storages = [] } = useGetStoragesQuery();

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Calculate time filter date
  const getTimeFilterDate = (filter: string): Date | null => {
    const now = new Date();
    switch (filter) {
      case "24h":
        return new Date(now.getTime() - 24 * 60 * 60 * 1000);
      case "48h":
        return new Date(now.getTime() - 48 * 60 * 60 * 1000);
      case "7d":
        return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      case "30d":
        return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      default:
        return null;
    }
  };

  // Filter files by time on client side (since backend doesn't support time filtering)
  const filteredFiles = useMemo(() => {
    if (!filesData?.items) return [];

    const timeFilterDate = getTimeFilterDate(selectedTimeFilter);
    if (!timeFilterDate) return filesData.items;

    return filesData.items.filter((file: IFile) => {
      const fileDate = new Date(file.createdAt);
      return fileDate >= timeFilterDate;
    });
  }, [filesData?.items, selectedTimeFilter]);

  // Fetch files when filters change
  useEffect(() => {
    const offset = (page - 1) * ITEMS_PER_PAGE;

    triggerQuery({
      limit: ITEMS_PER_PAGE,
      offset,
      q: debouncedSearch || undefined,
      status:
        selectedStatus !== "all" ? (selectedStatus as FileState) : undefined,
      vectorStoreId: selectedStorage !== "all" ? selectedStorage : undefined,
    });
  }, [page, debouncedSearch, selectedStatus, selectedStorage, triggerQuery]);

  // Storage options for select
  const storageOptions = [
    { value: "all", label: "Все хранилища" },
    ...storages.map((storage: IStorage) => ({
      value: storage.vectorStoreId,
      label: storage.name,
    })),
  ];

  // Calculate total pages based on filtered results
  const totalPages = Math.ceil((filesData?.total || 0) / ITEMS_PER_PAGE);

  // Format file size
  const formatFileSize = (bytes: number | null): string => {
    if (!bytes) return "N/A";
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(2)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(2)} MB`;
  };

  // Format date
  const formatDate = (dateString: string): string => {
    try {
      return format(new Date(dateString), "dd.MM.yyyy HH:mm");
    } catch {
      return dateString;
    }
  };

  // Table rows
  const rows = filteredFiles.map((file: IFile) => (
    <Table.Tr key={file.id}>
      <Table.Td>{file.id}</Table.Td>
      <Table.Td>
        <Tooltip
          label={file.s3ObjectKey || "No s3ObjectKey"}
          withArrow
          position="top-start"
          disabled={!file.s3ObjectKey}
        >
          <Text
            size="sm"
            style={{
              maxWidth: 300,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {file.name || "N/A"}
          </Text>
        </Tooltip>
      </Table.Td>

      <Table.Td>
        <Badge color={FILE_STATUS_COLORS[file.status]} variant="light">
          {file.status}
        </Badge>
      </Table.Td>
      <Table.Td>
        {storages.find((s: IStorage) => s.vectorStoreId === file.vectorStoreId)
          ?.name || "N/A"}
      </Table.Td>
      <Table.Td>{formatFileSize(file.size)}</Table.Td>
      <Table.Td>{formatDate(file.createdAt)}</Table.Td>
    </Table.Tr>
  ));

  return (
    <Stack gap="md">
      {/* Filters */}
      <Group gap="md">
        <TextInput
          placeholder="Поиск по названию..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.currentTarget.value)}
          style={{ flex: 1, maxWidth: 300 }}
        />

        <Select
          placeholder="Статус"
          data={STATUS_OPTIONS}
          value={selectedStatus}
          onChange={(value) => {
            setSelectedStatus(value || "all");
            setPage(1);
          }}
          style={{ width: 200 }}
          clearable={false}
        />

        <Select
          placeholder="Хранилище"
          data={storageOptions}
          value={selectedStorage}
          onChange={(value) => {
            setSelectedStorage(value || "all");
            setPage(1);
          }}
          style={{ width: 200 }}
          clearable={false}
        />

        <Select
          placeholder="Период"
          data={TIME_FILTER_OPTIONS}
          value={selectedTimeFilter}
          onChange={(value) => {
            setSelectedTimeFilter(value || "all");
            setPage(1);
          }}
          style={{ width: 200 }}
          clearable={false}
        />
      </Group>

      {/* Results info */}
      <Text size="sm" c="dimmed">
        {isLoading || isFetching ? (
          <Group gap="xs">
            <Loader size="xs" />
            <span>Загрузка...</span>
          </Group>
        ) : (
          `Найдено файлов: ${filesData?.total || 0}`
        )}
      </Text>

      {/* Table */}
      <div style={{ overflowX: "auto" }}>
        <Table striped highlightOnHover withTableBorder>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Название</Table.Th>
              <Table.Th>Статус</Table.Th>
              <Table.Th>Хранилище</Table.Th>
              <Table.Th>Размер</Table.Th>
              <Table.Th>Создано</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {isLoading || isFetching ? (
              <Table.Tr>
                <Table.Td
                  colSpan={6}
                  style={{ textAlign: "center", padding: "2rem" }}
                >
                  <Loader size="md" />
                </Table.Td>
              </Table.Tr>
            ) : rows.length > 0 ? (
              rows
            ) : (
              <Table.Tr>
                <Table.Td
                  colSpan={6}
                  style={{ textAlign: "center", padding: "2rem" }}
                >
                  <Text c="dimmed">Файлы не найдены</Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <Group justify="center" mt="md" mb="sm">
          <Pagination
            value={page}
            onChange={setPage}
            total={totalPages}
            siblings={1}
            boundaries={1}
          />
        </Group>
      )}
    </Stack>
  );
};
