import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { HabitsService } from "@/client"
import HabitActionsMenu from "@/components/Common/HabitActionsMenu"
import AddHabit from "@/components/Habits/AddHabit"
import HabitLogger from "@/components/Habits/HabitLogger"
import StreakDisplay from "@/components/Habits/StreakDisplay"
import PendingHabits from "@/components/Pending/PendingHabits"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const habitsSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getHabitsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      HabitsService.readHabits({
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["habits", { page }],
  }
}

export const Route = createFileRoute("/_layout/habits")({
  component: Habits,
  validateSearch: (search) => habitsSearchSchema.parse(search),
})

function HabitsTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getHabitsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const habits = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingHabits />
  }

  if (habits.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>You don't have any habits yet</EmptyState.Title>
            <EmptyState.Description>
              Add a new habit to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">Title</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Description</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Category</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Schedule</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Streak</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Log Today</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {habits?.map((habit) => (
            <Table.Row key={habit.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {habit.title}
              </Table.Cell>
              <Table.Cell
                color={!habit.description ? "gray" : "inherit"}
                truncate
                maxW="30%"
              >
                {habit.description || "N/A"}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {habit.category || "N/A"}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {String(habit.schedule?.type || "daily")}
              </Table.Cell>
              <Table.Cell>
                <StreakDisplay habitId={habit.id} />
              </Table.Cell>
              <Table.Cell>
                <HabitLogger habit={habit} />
              </Table.Cell>
              <Table.Cell>
                <HabitActionsMenu habit={habit} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function Habits() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Habits Management
      </Heading>
      <AddHabit />
      <HabitsTable />
    </Container>
  )
}
