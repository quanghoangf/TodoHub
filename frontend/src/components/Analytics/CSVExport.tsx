import {
  Button,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  HStack,
  Input,
  Select,
  Switch,
  Text,
  VStack,
  useToast,
} from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { format, subDays } from "date-fns"
import { useState } from "react"
import { FiDownload, FiLoader } from "react-icons/fi"

// Types based on analytics schemas
interface ExportRequest {
  habit_ids?: string[]
  start_date?: string
  end_date?: string
  include_metadata: boolean
}

interface ExportResponse {
  download_url: string
  filename: string
  total_records: number
  generated_at: string
}

interface HabitPublic {
  id: string
  title: string
  category?: string
}

interface CSVExportProps {
  habitId?: string // If provided, export only this habit
  userHabits?: HabitPublic[] // For multi-habit export
}

const CSVExport = ({ habitId, userHabits = [] }: CSVExportProps) => {
  const toast = useToast()

  // Form state
  const [selectedHabits, setSelectedHabits] = useState<string[]>(
    habitId ? [habitId] : [],
  )
  const [dateRange, setDateRange] = useState("last_30_days")
  const [customStartDate, setCustomStartDate] = useState("")
  const [customEndDate, setCustomEndDate] = useState("")
  const [includeMetadata, setIncludeMetadata] = useState(true)

  // Calculate date range based on selection
  const getDateRange = () => {
    const today = new Date()
    switch (dateRange) {
      case "last_7_days":
        return {
          start_date: format(subDays(today, 7), "yyyy-MM-dd"),
          end_date: format(today, "yyyy-MM-dd"),
        }
      case "last_30_days":
        return {
          start_date: format(subDays(today, 30), "yyyy-MM-dd"),
          end_date: format(today, "yyyy-MM-dd"),
        }
      case "last_90_days":
        return {
          start_date: format(subDays(today, 90), "yyyy-MM-dd"),
          end_date: format(today, "yyyy-MM-dd"),
        }
      case "last_year":
        return {
          start_date: format(subDays(today, 365), "yyyy-MM-dd"),
          end_date: format(today, "yyyy-MM-dd"),
        }
      case "custom":
        return {
          start_date: customStartDate || undefined,
          end_date: customEndDate || undefined,
        }
      default:
        return {
          start_date: undefined,
          end_date: undefined,
        }
    }
  }

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: async (
      exportRequest: ExportRequest,
    ): Promise<ExportResponse> => {
      const response = await fetch("/api/analytics/exports/csv", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(exportRequest),
      })

      if (!response.ok) {
        throw new Error("Export failed")
      }

      return response.json()
    },
    onSuccess: (data) => {
      // Trigger download
      const link = document.createElement("a")
      link.href = data.download_url
      link.download = data.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: "Export Successful",
        description: `Exported ${data.total_records} records to ${data.filename}`,
        status: "success",
        duration: 5000,
        isClosable: true,
      })
    },
    onError: (error) => {
      toast({
        title: "Export Failed",
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
    },
  })

  const handleExport = () => {
    const dates = getDateRange()
    const exportRequest: ExportRequest = {
      habit_ids: selectedHabits.length > 0 ? selectedHabits : undefined,
      start_date: dates.start_date,
      end_date: dates.end_date,
      include_metadata: includeMetadata,
    }

    exportMutation.mutate(exportRequest)
  }

  const isLoading = exportMutation.isPending

  return (
    <Card>
      <CardBody>
        <VStack align="stretch" gap={4}>
          <Text fontSize="md" fontWeight="semibold">
            Export Habit Data
          </Text>

          {/* Habit Selection - only show for multi-habit export */}
          {!habitId && userHabits.length > 0 && (
            <FormControl>
              <FormLabel fontSize="sm">
                Select Habits (leave empty for all)
              </FormLabel>
              <Select
                placeholder="Select habits to export..."
                value=""
                onChange={(e) => {
                  if (
                    e.target.value &&
                    !selectedHabits.includes(e.target.value)
                  ) {
                    setSelectedHabits([...selectedHabits, e.target.value])
                  }
                }}
              >
                {userHabits
                  .filter((habit) => !selectedHabits.includes(habit.id))
                  .map((habit) => (
                    <option key={habit.id} value={habit.id}>
                      {habit.title}{" "}
                      {habit.category ? `(${habit.category})` : ""}
                    </option>
                  ))}
              </Select>

              {selectedHabits.length > 0 && (
                <VStack align="stretch" gap={2} mt={2}>
                  <Text fontSize="xs" color="gray.600">
                    Selected habits:
                  </Text>
                  {selectedHabits.map((id) => {
                    const habit = userHabits.find((h) => h.id === id)
                    return habit ? (
                      <HStack key={id} justify="space-between">
                        <Text fontSize="sm">{habit.title}</Text>
                        <Button
                          size="xs"
                          variant="ghost"
                          onClick={() =>
                            setSelectedHabits((prev) =>
                              prev.filter((h) => h !== id),
                            )
                          }
                        >
                          Remove
                        </Button>
                      </HStack>
                    ) : null
                  })}
                </VStack>
              )}
            </FormControl>
          )}

          {/* Date Range Selection */}
          <FormControl>
            <FormLabel fontSize="sm">Date Range</FormLabel>
            <Select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
            >
              <option value="last_7_days">Last 7 days</option>
              <option value="last_30_days">Last 30 days</option>
              <option value="last_90_days">Last 90 days</option>
              <option value="last_year">Last year</option>
              <option value="all_time">All time</option>
              <option value="custom">Custom range</option>
            </Select>
          </FormControl>

          {/* Custom Date Range */}
          {dateRange === "custom" && (
            <HStack gap={4}>
              <FormControl>
                <FormLabel fontSize="sm">Start Date</FormLabel>
                <Input
                  type="date"
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                />
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm">End Date</FormLabel>
                <Input
                  type="date"
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                />
              </FormControl>
            </HStack>
          )}

          {/* Export Options */}
          <FormControl>
            <HStack justify="space-between">
              <FormLabel fontSize="sm" mb={0}>
                Include habit metadata
              </FormLabel>
              <Switch
                isChecked={includeMetadata}
                onChange={(e) => setIncludeMetadata(e.target.checked)}
              />
            </HStack>
            <Text fontSize="xs" color="gray.600" mt={1}>
              Includes habit descriptions and additional data
            </Text>
          </FormControl>

          {/* Export Button */}
          <Button
            leftIcon={
              isLoading ? <FiLoader className="animate-spin" /> : <FiDownload />
            }
            colorPalette="blue"
            onClick={handleExport}
            isDisabled={isLoading}
            loadingText="Exporting..."
          >
            {isLoading ? "Preparing Export..." : "Export to CSV"}
          </Button>

          {/* Export Info */}
          <Text fontSize="xs" color="gray.600">
            Export includes completion dates, recorded times, and habit details.
            Large exports may take a few moments to prepare.
          </Text>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default CSVExport
