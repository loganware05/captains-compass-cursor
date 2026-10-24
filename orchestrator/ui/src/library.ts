import { createLibrary } from "@openuidev/react-lang";
import {
  CloseoutLedgerWidget,
  CompassStatusBadge,
  ControlTowerTelemetry,
  HermeticScorecard,
  NorthStarStack,
  PlanApprovalCard,
  RecommendationCard,
} from "./components";

export const northstarOpenUILibrary = createLibrary({
  root: "NorthStarStack",
  components: [
    NorthStarStack,
    PlanApprovalCard,
    ControlTowerTelemetry,
    HermeticScorecard,
    CompassStatusBadge,
    CloseoutLedgerWidget,
    RecommendationCard,
  ],
});

export {
  CloseoutLedgerWidget,
  CompassStatusBadge,
  ControlTowerTelemetry,
  HermeticScorecard,
  NorthStarStack,
  PlanApprovalCard,
  RecommendationCard,
};
