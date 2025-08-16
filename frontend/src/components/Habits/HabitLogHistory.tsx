import { Badge, HStack, Text, VStack } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"

interface HabitLogHistoryProps {
  habitId: string
}

interface HabitLog {
  id: string
  habit_id: string
  user_id: string
  local_date: string
  recorded_at: string
  meta?: Record<string, any>
}

interface HabitLogsResponse {
  data: HabitLog[]
  count: number
}

const HabitLogHistory = ({ habitId }: HabitLogHistoryProps) => {
  const { data: logs, isLoading } = useQuery<HabitLogsResponse>({
    queryKey: ["habit-logs", habitId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/habits/${habitId}/logs?limit=30`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch habit logs")
      }

      return response.json()
    },
  })

  if (isLoading) {
    return (
      <Text fontSize="sm" color="gray.600">
        Loading history...
      </Text>
    )
  }

  if (!logs || logs.data.length === 0) {
    return (
      <VStack gap={2} align="center" p={4}>
        <Text fontSize="sm" color="gray.600">
          No logs yet. Start building your habit streak!
        </Text>
      </VStack>
    )
  }

  return (
    <VStack gap={3} align="stretch">
      <Text fontSize="sm" fontWeight="semibold" color="gray.700">
        Recent Activity ({logs.count} total logs)
      </Text>

      <VStack gap={2} align="stretch" maxH="200px" overflowY="auto">
        {logs.data.map((log) => (
          <HStack
            key={log.id}
            justify="space-between"
            p={2}
            bg="gray.50"
            borderRadius="md"
            fontSize="sm"
          >
            <Text fontWeight="medium">
              {format(new Date(log.local_date), "MMM dd, yyyy")}
            </Text>
            <Badge variant="solid" colorPalette="green" size="sm">
              Completed
            </Badge>
          </HStack>
        ))}
      </VStack>

      {logs.count > 30 && (
        <Text fontSize="xs" color="gray.500" textAlign="center">
          Showing latest 30 entries
        </Text>
      )}
    </VStack>
  )
}

export default HabitLogHistory
