import { z } from "zod"
import { QueryEngine } from "./types"

export type IQueryEngine = z.infer<typeof QueryEngine>
