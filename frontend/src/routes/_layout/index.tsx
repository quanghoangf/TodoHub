import {
  Badge,
  Box,
  Container,
  Grid,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

// Types based on analytics schemas
interface DashboardHabitOverview {
  habit_id: string
  title: string
  category?: string
  current_streak: number
  completion_rate_30_days: number
  last_completed?: string
  weekly_completions: number
}

interface DashboardResponse {
  user_id: string
  total_habits: number
  active_habits: number
  total_completions: number
  average_completion_rate: number
  longest_current_streak: number
  habits_overview: DashboardHabitOverview[]
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  // Query to fetch dashboard analytics
  const { data: dashboardData, isLoading } = useQuery<DashboardResponse>({
    queryKey: ["dashboard"],
    queryFn: async () => {
      // This will use the generated API client once analytics endpoints are available
      const response = await fetch("/api/v1/analytics/dashboard", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data")
      }
      return response.json()
    },
    enabled: !!currentUser,
  })

  return (
    <>
      <Container maxW="full">
        <VStack align="stretch" gap={8} pt={12} m={4}>
          {/* Welcome Section */}
          <Box>
            <Text fontSize="2xl" truncate maxW="sm">
              Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
            </Text>
            <Text>Welcome back, nice to see you again!</Text>
          </Box>

          {/* Analytics Overview */}
          {isLoading ? (
            <Text>Loading your analytics...</Text>
          ) : dashboardData ? (
            <VStack align="stretch" gap={6}>
              {/* Key Metrics */}
              <Box>
                <Text fontSize="lg" fontWeight="semibold" mb={4}>
                  Your Progress Overview
                </Text>
                <Grid
                  templateColumns="repeat(auto-fit, minmax(200px, 1fr))"
                  gap={4}
                >
                  <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
                    <VStack align="start" gap={2}>
                      <Text fontSize="sm" color="gray.600">Total Habits</Text>
                      <Text fontSize="2xl" fontWeight="bold">{dashboardData.total_habits}</Text>
                      <Text fontSize="xs" color="gray.500">
                        {dashboardData.active_habits} active in last 30 days
                      </Text>
                    </VStack>
                  </Box>

                  <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
                    <VStack align="start" gap={2}>
                      <Text fontSize="sm" color="gray.600">Total Completions</Text>
                      <Text fontSize="2xl" fontWeight="bold">
                        {dashboardData.total_completions}
                      </Text>
                      <Text fontSize="xs" color="gray.500">All time</Text>
                    </VStack>
                  </Box>

                  <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
                    <VStack align="start" gap={2}>
                      <Text fontSize="sm" color="gray.600">Average Completion Rate</Text>
                      <Text fontSize="2xl" fontWeight="bold">
                        {Math.round(
                          dashboardData.average_completion_rate * 100,
                        )}
                        %
                      </Text>
                      <Text fontSize="xs" color="gray.500">Across all habits</Text>
                    </VStack>
                  </Box>

                  <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
                    <VStack align="start" gap={2}>
                      <Text fontSize="sm" color="gray.600">Longest Current Streak</Text>
                      <Text fontSize="2xl" fontWeight="bold">
                        {dashboardData.longest_current_streak}{" "}
                        <Text as="span" fontSize="md" color="gray.600">
                          days
                        </Text>
                      </Text>
                      <Text fontSize="xs" color="gray.500">Your best current streak</Text>
                    </VStack>
                  </Box>
                </Grid>
              </Box>

              {/* Habits Overview */}
              {dashboardData.habits_overview.length > 0 && (
                <Box>
                  <Text fontSize="lg" fontWeight="semibold" mb={4}>
                    Your Habits at a Glance
                  </Text>
                  <Grid
                    templateColumns="repeat(auto-fit, minmax(300px, 1fr))"
                    gap={4}
                  >
                    {dashboardData.habits_overview.slice(0, 6).map((habit) => (
                      <Box key={habit.habit_id} bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
                        <VStack align="stretch" gap={3}>
                          <HStack justify="space-between" align="start">
                            <VStack align="start" gap={1}>
                              <Text
                                fontWeight="semibold"
                                truncate
                                maxW="200px"
                              >
                                {habit.title}
                              </Text>
                              {habit.category && (
                                <Badge
                                  size="sm"
                                  colorPalette="blue"
                                  variant="subtle"
                                >
                                  {habit.category}
                                </Badge>
                              )}
                            </VStack>
                            <Text fontSize="sm" color="gray.600">
                              {Math.round(
                                habit.completion_rate_30_days * 100,
                              )}
                              %
                            </Text>
                          </HStack>

                          <HStack justify="space-between" fontSize="sm">
                            <VStack align="start" gap={0}>
                              <Text color="gray.600">Current Streak</Text>
                              <Text fontWeight="semibold">
                                {habit.current_streak} days
                              </Text>
                            </VStack>
                            <VStack align="end" gap={0}>
                              <Text color="gray.600">This Week</Text>
                              <Text fontWeight="semibold">
                                {habit.weekly_completions} times
                              </Text>
                            </VStack>
                          </HStack>

                          {habit.last_completed && (
                            <Text fontSize="xs" color="gray.500">
                              Last completed:{" "}
                              {new Date(
                                habit.last_completed,
                              ).toLocaleDateString()}
                            </Text>
                          )}
                        </VStack>
                      </Box>
                    ))}
                  </Grid>

                  {dashboardData.habits_overview.length > 6 && (
                    <Text fontSize="sm" color="gray.600" mt={2}>
                      And {dashboardData.habits_overview.length - 6} more
                      habits...
                    </Text>
                  )}
                </Box>
              )}
            </VStack>
          ) : (
            <Box>
              <Text fontSize="lg" fontWeight="semibold" mb={2}>
                Start Building Great Habits! 🎯
              </Text>
              <Text color="gray.600">
                Create your first habit to see your progress analytics here.
              </Text>
            </Box>
          )}
        </VStack>
      </Container>
    </>
  )
}
