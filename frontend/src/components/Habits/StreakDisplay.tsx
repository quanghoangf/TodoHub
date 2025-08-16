import { Badge, HStack, Text, VStack } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { FiTarget, FiTrendingUp } from "react-icons/fi"

interface StreakDisplayProps {
  habitId: string
}

interface StreakData {
  habit_id: string
  current_streak: number
  longest_streak: number
  last_updated: string
}

const StreakDisplay = ({ habitId }: StreakDisplayProps) => {
  const { data: streak, isLoading } = useQuery<StreakData>({
    queryKey: ["habit-streak", habitId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/habits/${habitId}/streak`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch streak data')
      }
      
      return response.json()
    },
  })

  if (isLoading) {
    return (
      <HStack gap={4}>
        <Badge variant="subtle" colorPalette="gray">
          Loading...
        </Badge>
      </HStack>
    )
  }

  if (!streak) {
    return null
  }

  return (
    <HStack gap={4} wrap="wrap">
      <VStack gap={1} align="center">
        <HStack gap={1}>
          <FiTarget color="orange" />
          <Text fontSize="xs" color="gray.600">
            Current Streak
          </Text>
        </HStack>
        <Badge variant="solid" colorPalette="orange" size="lg">
          {streak.current_streak} days
        </Badge>
      </VStack>
      
      <VStack gap={1} align="center">
        <HStack gap={1}>
          <FiTrendingUp color="green" />
          <Text fontSize="xs" color="gray.600">
            Best Streak
          </Text>
        </HStack>
        <Badge variant="solid" colorPalette="green" size="lg">
          {streak.longest_streak} days
        </Badge>
      </VStack>
    </HStack>
  )
}

export default StreakDisplay