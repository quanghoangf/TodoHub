import {
  Badge,
  Box,
  Card,
  CardBody,
  Grid,
  HStack,
  Text,
  VStack,
  useColorModeValue,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"

// Types based on analytics schemas
interface CompletionStats {
  total_completions: number
  completion_rate: number
  current_streak: number
  longest_streak: number
  average_completions_per_week: number
}

interface WeekdayStats {
  monday: number
  tuesday: number
  wednesday: number
  thursday: number
  friday: number
  saturday: number
  sunday: number
}

interface MonthlyTrend {
  month: string
  completions: number
  completion_rate: number
}

interface HabitSummaryResponse {
  habit_id: string
  habit_title: string
  habit_category?: string
  start_date?: string
  completion_stats: CompletionStats
  weekday_stats: WeekdayStats
  monthly_trends: MonthlyTrend[]
  best_streak_period?: {
    start: string
    end: string
  }
}

interface AnalyticsSummaryProps {
  habitId: string
}

const AnalyticsSummary = ({ habitId }: AnalyticsSummaryProps) => {
  const cardBg = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.600")
  const textColor = useColorModeValue("gray.600", "gray.400")

  // Query to fetch analytics summary
  const {
    data: summary,
    isLoading,
    error,
  } = useQuery<HabitSummaryResponse>({
    queryKey: ["habitSummary", habitId],
    queryFn: async () => {
      // This will use the generated API client once analytics endpoints are available
      const response = await fetch(`/api/v1/analytics/habits/${habitId}/summary`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) {
        throw new Error("Failed to fetch habit summary")
      }
      return response.json()
    },
    enabled: !!habitId,
  })

  if (isLoading) {
    return (
      <VStack align="stretch" gap={4}>
        <Text fontSize="sm" color={textColor}>
          Loading analytics...
        </Text>
        <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} bg={cardBg} borderColor={borderColor}>
              <CardBody>
                <Box h="80px" bg="gray.100" borderRadius="md" />
              </CardBody>
            </Card>
          ))}
        </Grid>
      </VStack>
    )
  }

  if (error || !summary) {
    return (
      <Text fontSize="sm" color="red.500">
        Failed to load analytics data
      </Text>
    )
  }

  const { completion_stats, weekday_stats, monthly_trends } = summary

  // Calculate best performing day
  const weekdays = [
    { name: "Monday", value: weekday_stats.monday },
    { name: "Tuesday", value: weekday_stats.tuesday },
    { name: "Wednesday", value: weekday_stats.wednesday },
    { name: "Thursday", value: weekday_stats.thursday },
    { name: "Friday", value: weekday_stats.friday },
    { name: "Saturday", value: weekday_stats.saturday },
    { name: "Sunday", value: weekday_stats.sunday },
  ]

  const bestDay = weekdays.reduce((best, current) =>
    current.value > best.value ? current : best,
  )

  // Get latest trend
  const latestTrend = monthly_trends[monthly_trends.length - 1]
  const previousTrend = monthly_trends[monthly_trends.length - 2]
  const trendDirection =
    latestTrend && previousTrend
      ? latestTrend.completion_rate > previousTrend.completion_rate
        ? "increase"
        : "decrease"
      : null

  return (
    <VStack align="stretch" gap={6}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <VStack align="start" gap={1}>
          <Text fontSize="lg" fontWeight="bold">
            Analytics Summary
          </Text>
          <Text fontSize="sm" color={textColor}>
            {summary.habit_title}
          </Text>
        </VStack>
        {summary.habit_category && (
          <Badge colorPalette="blue" variant="subtle">
            {summary.habit_category}
          </Badge>
        )}
      </HStack>

      {/* Key Statistics */}
      <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
        {/* Total Completions */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="start" gap={2}>
              <Text fontSize="sm" color={textColor}>Total Completions</Text>
              <Text fontSize="2xl" fontWeight="bold">{completion_stats.total_completions}</Text>
              <Text fontSize="xs" color={textColor}>
                {Math.round(completion_stats.completion_rate * 100)}% completion
                rate
              </Text>
            </VStack>
          </CardBody>
        </Card>

        {/* Current Streak */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="start" gap={2}>
              <Text fontSize="sm" color={textColor}>Current Streak</Text>
              <Text fontSize="2xl" fontWeight="bold">
                {completion_stats.current_streak}{" "}
                <Text as="span" fontSize="md" color={textColor}>
                  days
                </Text>
              </Text>
              <Text fontSize="xs" color={textColor}>
                Longest: {completion_stats.longest_streak} days
              </Text>
            </VStack>
          </CardBody>
        </Card>

        {/* Weekly Average */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="start" gap={2}>
              <Text fontSize="sm" color={textColor}>Weekly Average</Text>
              <Text fontSize="2xl" fontWeight="bold">
                {completion_stats.average_completions_per_week.toFixed(1)}
              </Text>
              <Text fontSize="xs" color={textColor}>completions per week</Text>
            </VStack>
          </CardBody>
        </Card>

        {/* Recent Trend */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="start" gap={2}>
              <Text fontSize="sm" color={textColor}>Recent Trend</Text>
              <Text fontSize="2xl" fontWeight="bold">
                {latestTrend
                  ? Math.round(latestTrend.completion_rate * 100)
                  : 0}
                %
              </Text>
              <Text fontSize="xs" color={textColor}>
                {trendDirection && (
                  <Text as="span" color={trendDirection === "increase" ? "green.500" : "red.500"}>
                    {trendDirection === "increase" ? "↗" : "↘"}{" "}
                  </Text>
                )}
                {latestTrend
                  ? format(new Date(`${latestTrend.month}-01`), "MMM yyyy")
                  : "No data"}
              </Text>
            </VStack>
          </CardBody>
        </Card>
      </Grid>

      {/* Weekday Performance */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardBody>
          <VStack align="stretch" gap={4}>
            <Text fontSize="md" fontWeight="semibold">
              Day of Week Performance
            </Text>
            <Grid templateColumns="repeat(7, 1fr)" gap={2}>
              {weekdays.map((day) => {
                const isMax = day.value === bestDay.value && day.value > 0
                return (
                  <VStack key={day.name} gap={2}>
                    <Text fontSize="xs" color={textColor} textAlign="center">
                      {day.name.slice(0, 3)}
                    </Text>
                    <Box
                      h="60px"
                      bg={isMax ? "green.400" : "gray.200"}
                      borderRadius="md"
                      position="relative"
                      display="flex"
                      alignItems="end"
                      justifyContent="center"
                      p={1}
                    >
                      <Text
                        fontSize="xs"
                        fontWeight="bold"
                        color={isMax ? "white" : "gray.600"}
                      >
                        {day.value}
                      </Text>
                    </Box>
                  </VStack>
                )
              })}
            </Grid>
            <Text fontSize="xs" color={textColor} textAlign="center">
              Best day: {bestDay.name} ({bestDay.value} completions)
            </Text>
          </VStack>
        </CardBody>
      </Card>

      {/* Monthly Trends */}
      {monthly_trends.length > 0 && (
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="stretch" gap={4}>
              <Text fontSize="md" fontWeight="semibold">
                Monthly Trends (Last 6 months)
              </Text>
              <Grid
                templateColumns="repeat(auto-fit, minmax(120px, 1fr))"
                gap={3}
              >
                {monthly_trends.slice(-6).map((trend) => (
                  <VStack key={trend.month} gap={1} align="center">
                    <Text fontSize="xs" color={textColor}>
                      {format(new Date(`${trend.month}-01`), "MMM")}
                    </Text>
                    <Text fontSize="lg" fontWeight="bold">
                      {trend.completions}
                    </Text>
                    <Text fontSize="xs" color={textColor}>
                      {Math.round(trend.completion_rate * 100)}%
                    </Text>
                  </VStack>
                ))}
              </Grid>
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Best Streak Period */}
      {summary.best_streak_period && completion_stats.longest_streak > 0 && (
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack align="stretch" gap={3}>
              <Text fontSize="md" fontWeight="semibold">
                Best Streak Period
              </Text>
              <HStack justify="space-between">
                <VStack align="start" gap={1}>
                  <Text fontSize="sm" color={textColor}>
                    Duration
                  </Text>
                  <Text fontSize="lg" fontWeight="bold">
                    {completion_stats.longest_streak} days
                  </Text>
                </VStack>
                <VStack align="end" gap={1}>
                  <Text fontSize="sm" color={textColor}>
                    Period
                  </Text>
                  <Text fontSize="sm">
                    {format(
                      new Date(summary.best_streak_period.start),
                      "MMM d",
                    )}{" "}
                    -{" "}
                    {format(
                      new Date(summary.best_streak_period.end),
                      "MMM d, yyyy",
                    )}
                  </Text>
                </VStack>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      )}
    </VStack>
  )
}

export default AnalyticsSummary
