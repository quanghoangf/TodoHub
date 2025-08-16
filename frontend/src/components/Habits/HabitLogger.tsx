import { Button, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

import type { HabitPublic } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"

interface HabitLoggerProps {
  habit: HabitPublic
}

interface HabitLogData {
  local_date: string
  meta?: Record<string, any>
}

const HabitLogger = ({ habit }: HabitLoggerProps) => {
  const [isLogged, setIsLogged] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const logHabitMutation = useMutation({
    mutationFn: async (logData: HabitLogData) => {
      // Manual API call since the client hasn't been generated yet
      const response = await fetch(`/api/v1/habits/${habit.id}/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(logData),
      })
      
      if (!response.ok) {
        throw new Error('Failed to log habit')
      }
      
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Habit logged successfully!")
      setIsLogged(true)
      queryClient.invalidateQueries({ queryKey: ["habits"] })
      queryClient.invalidateQueries({ queryKey: ["habit-logs", habit.id] })
      queryClient.invalidateQueries({ queryKey: ["habit-streak", habit.id] })
    },
    onError: () => {
      showErrorToast("Failed to log habit. Please try again.")
    },
  })

  const handleLogHabit = () => {
    const today = new Date().toISOString().split('T')[0] // YYYY-MM-DD format
    logHabitMutation.mutate({
      local_date: today,
      meta: { logged_at: new Date().toISOString() }
    })
  }

  return (
    <VStack gap={2} align="stretch">
      <Button
        variant={isLogged ? "solid" : "outline"}
        colorPalette={isLogged ? "green" : "blue"}
        onClick={handleLogHabit}
        loading={logHabitMutation.isPending}
        disabled={isLogged}
        size="sm"
      >
        {isLogged ? "Logged Today!" : "Log Today"}
      </Button>
      
      {isLogged && (
        <Text fontSize="xs" color="green.600" textAlign="center">
          Great job! Keep up the streak! 🎉
        </Text>
      )}
    </VStack>
  )
}

export default HabitLogger