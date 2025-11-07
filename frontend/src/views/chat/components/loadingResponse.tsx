import {
    Avatar,
    Box,
    Flex,
    Paper,
    useMantineTheme,
} from "@mantine/core"

export const LoadingResponse = () => {
    const theme = useMantineTheme()

    return (
        <Flex align="flex-start" gap="md" mb="lg" maw="80%">
            <Avatar color="blue" alt="AI" radius="xl">AI</Avatar>
            <Box>
                <Paper p="md" radius="md" bg={theme.colors.gray[1]}>
                    <Flex gap="sm">
                        <Box
                            className="animate-bounce"
                            style={{
                                width: 8,
                                height: 8,
                                borderRadius: "50%",
                                background: theme.colors.gray[6],
                            }}
                        />
                        <Box
                            className="animate-bounce delay-75"
                            style={{
                                width: 8,
                                height: 8,
                                borderRadius: "50%",
                                background: theme.colors.gray[6],
                                animationDelay: "0.2s",
                            }}
                        />
                        <Box
                            className="animate-bounce delay-150"
                            style={{
                                width: 8,
                                height: 8,
                                borderRadius: "50%",
                                background: theme.colors.gray[6],
                                animationDelay: "0.4s",
                            }}
                        />
                    </Flex>
                </Paper>
            </Box>
        </Flex>
    )
}