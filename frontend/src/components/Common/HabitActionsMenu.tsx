import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { HabitPublic } from "@/client"
import DeleteHabit from "../Habits/DeleteHabit"
import EditHabit from "../Habits/EditHabit"
import ViewHabitDetails from "../Habits/ViewHabitDetails"

interface HabitActionsMenuProps {
  habit: HabitPublic
}

const HabitActionsMenu = ({ habit }: HabitActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <ViewHabitDetails habit={habit} />
        <EditHabit habit={habit} />
        <DeleteHabit id={habit.id} />
      </MenuContent>
    </MenuRoot>
  )
}

export default HabitActionsMenu
