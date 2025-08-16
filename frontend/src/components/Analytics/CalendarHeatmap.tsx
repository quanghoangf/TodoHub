import {
  Box,
  Grid,
  HStack,
  Text,
  Tooltip,
  VStack,
  useColorModeValue,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { addDays, format, isSameMonth, isToday, startOfWeek } from "date-fns"

// Types based on analytics schemas
interface HeatmapDataPoint {
  date: string
  value: number
  level: number // 0-4 intensity level
}

interface HeatmapResponse {
  habit_id: string
  start_date: string
  end_date: string
  data: HeatmapDataPoint[]
  total_days: number
  completed_days: number
}

interface CalendarHeatmapProps {
  habitId: string
  daysBack?: number
}

const CalendarHeatmap = ({ habitId, daysBack = 365 }: CalendarHeatmapProps) => {
  // Color scheme for different intensity levels
  const colorScheme = useColorModeValue(
    {
      0: "gray.100", // No activity
      1: "green.100", // Low activity
      2: "green.200", // Medium-low activity
      3: "green.400", // Medium-high activity
      4: "green.600", // High activity
    },
    {
      0: "gray.800", // No activity (dark mode)
      1: "green.800", // Low activity (dark mode)
      2: "green.700", // Medium-low activity (dark mode)
      3: "green.500", // Medium-high activity (dark mode)
      4: "green.300", // High activity (dark mode)
    },
  )

  const borderColor = useColorModeValue("gray.200", "gray.600")
  const textColor = useColorModeValue("gray.600", "gray.400")

  // Query to fetch heatmap data
  const {
    data: heatmapData,
    isLoading,
    error,
  } = useQuery<HeatmapResponse>({
    queryKey: ["heatmap", habitId, daysBack],
    queryFn: async () => {
      // This will use the generated API client once analytics endpoints are available
      const response = await fetch(
        `/api/analytics/habits/${habitId}/heatmap?days_back=${daysBack}`,
      )
      if (!response.ok) {
        throw new Error("Failed to fetch heatmap data")
      }
      return response.json()
    },
    enabled: !!habitId,
  })

  if (isLoading) {
    return (
      <VStack align="stretch" gap={4}>
        <Text fontSize="sm" color={textColor}>
          Loading heatmap...
        </Text>
        <Box h="150px" bg="gray.100" borderRadius="md" />
      </VStack>
    )
  }

  if (error || !heatmapData) {
    return (
      <Text fontSize="sm" color="red.500">
        Failed to load heatmap data
      </Text>
    )
  }

  // Create a map for quick lookup of completion data
  const dataMap = new Map<string, HeatmapDataPoint>()
  heatmapData.data.forEach((point) => {
    dataMap.set(point.date, point)
  })

  // Generate grid data - group by weeks
  const startDate = new Date(heatmapData.start_date)
  const endDate = new Date(heatmapData.end_date)
  const weeks: Date[][] = []

  let currentWeekStart = startOfWeek(startDate, { weekStartsOn: 0 }) // Start on Sunday

  while (currentWeekStart <= endDate) {
    const week: Date[] = []
    for (let i = 0; i < 7; i++) {
      const day = addDays(currentWeekStart, i)
      if (day >= startDate && day <= endDate) {
        week.push(day)
      } else {
        week.push(null) // Empty cell for days outside range
      }
    }
    weeks.push(week)
    currentWeekStart = addDays(currentWeekStart, 7)
  }

  // Month labels for the top of the calendar
  const monthLabels = []
  const currentMonth = new Date(startDate)
  while (currentMonth <= endDate) {
    monthLabels.push(format(currentMonth, "MMM"))
    currentMonth.setMonth(currentMonth.getMonth() + 1)
  }

  const completionRate =
    heatmapData.total_days > 0
      ? Math.round((heatmapData.completed_days / heatmapData.total_days) * 100)
      : 0

  return (
    <VStack align="stretch" gap={4} p={4}>
      {/* Header with stats */}
      <HStack justify="space-between" align="center">
        <Text fontSize="md" fontWeight="semibold">
          Activity Calendar
        </Text>
        <Text fontSize="sm" color={textColor}>
          {heatmapData.completed_days} days completed ({completionRate}%)
        </Text>
      </HStack>

      {/* Calendar grid */}
      <Box>
        {/* Month labels */}
        <HStack gap={1} mb={2} ml="20px">
          {monthLabels.map((month, index) => (
            <Text
              key={index}
              fontSize="xs"
              color={textColor}
              minW="60px"
              textAlign="left"
            >
              {month}
            </Text>
          ))}
        </HStack>

        {/* Day labels and grid */}
        <HStack align="start" gap={1}>
          {/* Day of week labels */}
          <VStack gap={1} minW="18px">
            <Text fontSize="xs" h="12px" />
            {["S", "M", "T", "W", "T", "F", "S"].map((day, index) => (
              <Text
                key={index}
                fontSize="xs"
                color={textColor}
                h="12px"
                lineHeight="12px"
                textAlign="center"
              >
                {index % 2 === 1 ? day : ""}{" "}
                {/* Show only M, W, F for spacing */}
              </Text>
            ))}
          </VStack>

          {/* Heatmap grid */}
          <Grid
            templateColumns={`repeat(${weeks.length}, 1fr)`}
            gap={1}
            flex={1}
          >
            {weeks.map((week, weekIndex) =>
              week.map((day, dayIndex) => {
                if (!day) {
                  return (
                    <Box key={`${weekIndex}-${dayIndex}`} w="12px" h="12px" />
                  )
                }

                const dateString = format(day, "yyyy-MM-dd")
                const dataPoint = dataMap.get(dateString)
                const level = dataPoint?.level || 0
                const value = dataPoint?.value || 0

                return (
                  <Tooltip
                    key={`${weekIndex}-${dayIndex}`}
                    label={`${format(day, "MMM d, yyyy")}: ${value} completion${value !== 1 ? "s" : ""}`}
                    placement="top"
                  >
                    <Box
                      w="12px"
                      h="12px"
                      bg={colorScheme[level]}
                      border="1px solid"
                      borderColor={borderColor}
                      borderRadius="1px"
                      cursor="pointer"
                      position="relative"
                      _hover={{
                        transform: "scale(1.1)",
                        zIndex: 1,
                      }}
                      transition="transform 0.1s"
                      outline={isToday(day) ? "2px solid" : "none"}
                      outlineColor={isToday(day) ? "blue.500" : "transparent"}
                      outlineOffset={isToday(day) ? "1px" : "0"}
                    />
                  </Tooltip>
                )
              }),
            )}
          </Grid>
        </HStack>
      </Box>

      {/* Legend */}
      <HStack
        justify="space-between"
        align="center"
        fontSize="xs"
        color={textColor}
      >
        <Text>Less</Text>
        <HStack gap={1}>
          {[0, 1, 2, 3, 4].map((level) => (
            <Box
              key={level}
              w="10px"
              h="10px"
              bg={colorScheme[level]}
              border="1px solid"
              borderColor={borderColor}
              borderRadius="1px"
            />
          ))}
        </HStack>
        <Text>More</Text>
      </HStack>
    </VStack>
  )
}

export default CalendarHeatmap
