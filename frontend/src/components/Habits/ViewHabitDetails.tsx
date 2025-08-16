import {
  Button,
  DialogActionTrigger,
  HStack,
  Separator,
  Tabs,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FiEye } from "react-icons/fi"

import type { HabitPublic } from "@/client"
import SimpleAnalytics from "../Analytics/SimpleAnalytics"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import HabitLogHistory from "./HabitLogHistory"
import StreakDisplay from "./StreakDisplay"

interface ViewHabitDetailsProps {
  habit: HabitPublic
}

const ViewHabitDetails = ({ habit }: ViewHabitDetailsProps) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <DialogRoot
      size={{ base: "xs", md: "lg" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">
          <FiEye fontSize="16px" />
          View Details
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{habit.title}</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <Tabs.Root defaultValue="overview" variant="subtle">
            <Tabs.List>
              <Tabs.Trigger value="overview">Overview</Tabs.Trigger>
              <Tabs.Trigger value="analytics">Analytics</Tabs.Trigger>
              <Tabs.Trigger value="history">History</Tabs.Trigger>
              <Tabs.Trigger value="export">Export</Tabs.Trigger>
            </Tabs.List>

            {/* Overview Tab */}
            <Tabs.Content value="overview">
              <VStack gap={6} align="stretch" pt={4}>
                {/* Basic Info */}
                <VStack gap={3} align="stretch">
                  <Text fontSize="sm" color="gray.600">
                    <strong>Description:</strong>{" "}
                    {habit.description || "No description"}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    <strong>Category:</strong>{" "}
                    {habit.category || "Uncategorized"}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    <strong>Schedule:</strong>{" "}
                    {String(habit.schedule?.type || "daily")}
                  </Text>
                  {habit.start_date && (
                    <Text fontSize="sm" color="gray.600">
                      <strong>Started:</strong>{" "}
                      {new Date(habit.start_date).toLocaleDateString()}
                    </Text>
                  )}
                </VStack>

                <Separator />

                {/* Streak Information */}
                <VStack gap={3} align="stretch">
                  <Text fontSize="md" fontWeight="semibold">
                    Streak Progress
                  </Text>
                  <HStack justify="center">
                    <StreakDisplay habitId={habit.id} />
                  </HStack>
                </VStack>
              </VStack>
            </Tabs.Content>

            {/* Analytics Tab */}
            <Tabs.Content value="analytics">
              <SimpleAnalytics habitId={habit.id} />
            </Tabs.Content>

            {/* History Tab */}
            <Tabs.Content value="history">
              <VStack gap={3} align="stretch" pt={4}>
                <Text fontSize="md" fontWeight="semibold">
                  Completion History
                </Text>
                <HabitLogHistory habitId={habit.id} />
              </VStack>
            </Tabs.Content>

            {/* Export Tab */}
            <Tabs.Content value="export">
              <VStack gap={3} align="stretch" pt={4}>
                <Text fontSize="sm" color="gray.600">
                  Export functionality will be available once the analytics backend is running.
                </Text>
              </VStack>
            </Tabs.Content>
          </Tabs.Root>
        </DialogBody>

        <DialogFooter>
          <DialogActionTrigger asChild>
            <Button variant="subtle" colorPalette="gray">
              Close
            </Button>
          </DialogActionTrigger>
        </DialogFooter>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default ViewHabitDetails
