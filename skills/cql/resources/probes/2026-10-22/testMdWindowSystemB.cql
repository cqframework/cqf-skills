library testMdWindowSystemB version '1.0.0'

define function FollowUpWindow(P Interval<DateTime>):
  Interval[start of P, end of P + 7 days]

define Stay: Interval[@2025-01-17T10:00:00.000Z, @2025-01-17T14:00:00.000Z]
define "Window": FollowUpWindow(Stay)
define "Day3 InWindow": @2025-01-20T14:00:00.000Z in FollowUpWindow(Stay)
define "Day7 InWindow": @2025-01-24T14:00:00.000Z in FollowUpWindow(Stay)
define "Day8 InWindow": @2025-01-24T14:00:00.001Z in FollowUpWindow(Stay)
define "BeforeStay InWindow": @2025-01-17T09:59:59.999Z in FollowUpWindow(Stay)
define "Precedence": end of Stay + 7 days
