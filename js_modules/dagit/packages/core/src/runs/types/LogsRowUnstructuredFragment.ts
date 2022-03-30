/* tslint:disable */
/* eslint-disable */
// @generated
// This file was automatically generated and should not be edited.

import { LogLevel } from "./../../types/globalTypes";

// ====================================================
// GraphQL fragment: LogsRowUnstructuredFragment
// ====================================================

export interface LogsRowUnstructuredFragment {
  __typename: "ExecutionStepFailureEvent" | "ExecutionStepInputEvent" | "ExecutionStepOutputEvent" | "ExecutionStepSkippedEvent" | "ExecutionStepStartEvent" | "ExecutionStepSuccessEvent" | "ExecutionStepUpForRetryEvent" | "ExecutionStepRestartEvent" | "LogMessageEvent" | "RunFailureEvent" | "RunStartEvent" | "RunEnqueuedEvent" | "RunDequeuedEvent" | "RunStartingEvent" | "RunCancelingEvent" | "RunCanceledEvent" | "RunSuccessEvent" | "HandledOutputEvent" | "LoadedInputEvent" | "LogsCapturedEvent" | "ObjectStoreOperationEvent" | "StepExpectationResultEvent" | "MaterializationEvent" | "ObservationEvent" | "EngineEvent" | "HookCompletedEvent" | "HookSkippedEvent" | "HookErroredEvent" | "AlertStartEvent" | "AlertSuccessEvent" | "AlertFailureEvent";
  message: string;
  timestamp: string;
  level: LogLevel;
  stepKey: string | null;
}
