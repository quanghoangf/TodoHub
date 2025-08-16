import {
  Box,
  Text,
  VStack,
  Grid,
} from "@chakra-ui/react"

// Simple analytics component using only basic Chakra components
interface SimpleAnalyticsProps {
  habitId: string
}

const SimpleAnalytics = ({ habitId: _ }: SimpleAnalyticsProps) => {
  // For now, just show a placeholder since the backend isn't running
  return (
    <VStack align="stretch" gap={6} p={4}>
      {/* Header */}
      <Text fontSize="lg" fontWeight="bold">
        Analytics Dashboard
      </Text>

      {/* Placeholder metrics */}
      <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
        <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
          <VStack align="start" gap={2}>
            <Text fontSize="sm" color="gray.600">Total Completions</Text>
            <Text fontSize="2xl" fontWeight="bold">--</Text>
            <Text fontSize="xs" color="gray.500">Loading...</Text>
          </VStack>
        </Box>

        <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
          <VStack align="start" gap={2}>
            <Text fontSize="sm" color="gray.600">Current Streak</Text>
            <Text fontSize="2xl" fontWeight="bold">-- days</Text>
            <Text fontSize="xs" color="gray.500">Loading...</Text>
          </VStack>
        </Box>

        <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
          <VStack align="start" gap={2}>
            <Text fontSize="sm" color="gray.600">Completion Rate</Text>
            <Text fontSize="2xl" fontWeight="bold">--%</Text>
            <Text fontSize="xs" color="gray.500">Loading...</Text>
          </VStack>
        </Box>
      </Grid>

      {/* Heatmap placeholder */}
      <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
        <VStack align="stretch" gap={4}>
          <Text fontSize="md" fontWeight="semibold">Activity Calendar</Text>
          <Box h="150px" bg="gray.50" borderRadius="md" display="flex" alignItems="center" justifyContent="center">
            <Text color="gray.500">Calendar heatmap will appear here</Text>
          </Box>
        </VStack>
      </Box>

      {/* Export placeholder */}
      <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
        <VStack align="stretch" gap={4}>
          <Text fontSize="md" fontWeight="semibold">Export Data</Text>
          <Text fontSize="sm" color="gray.600">
            Analytics and export functionality is available once the backend is running.
          </Text>
        </VStack>
      </Box>
    </VStack>
  )
}

export default SimpleAnalytics