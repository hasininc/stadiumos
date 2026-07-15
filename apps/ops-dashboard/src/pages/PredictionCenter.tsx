import React, { useState, useEffect } from 'react';
import { useOpsStore } from '../store/opsStore';
import { useCrowdPrediction } from '../hooks/useCrowdPrediction';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  Cpu,
  RefreshCw,
  Sliders,
  AlertTriangle,
  Clock,
  Shield,
  Activity,
  Users,
  Sun,
  CloudRain,
  Activity as AnomalyIcon,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  BarChart,
  Bar,
  LineChart,
  Line,
  CartesianGrid,
  Legend,
} from 'recharts';

// ──────────────────────────────────────────────
// Static Analytics Chart Data
// ──────────────────────────────────────────────
const historicalAttendanceData = [
  { time: '17:00', attendance: 12000, accuracy: 96.5, risk: 20 },
  { time: '17:15', attendance: 25000, accuracy: 97.1, risk: 35 },
  { time: '17:30', attendance: 42000, accuracy: 97.8, risk: 50 },
  { time: '17:45', attendance: 61000, accuracy: 98.2, risk: 65 },
  { time: '18:00', attendance: 73000, accuracy: 98.5, risk: 78 },
  { time: 'Live', attendance: 78550, accuracy: 97.2, risk: 84 },
];

const queueTimeTrendData = [
  { time: '17:00', gateA: 8, gateB: 12, gateC: 5, gateD: 6 },
  { time: '17:15', gateA: 14, gateB: 19, gateC: 9, gateD: 8 },
  { time: '17:30', gateA: 22, gateB: 28, gateC: 16, gateD: 11 },
  { time: '17:45', gateA: 19, gateB: 35, gateC: 22, gateD: 15 },
  { time: '18:00', gateA: 15, gateB: 42, gateC: 31, gateD: 18 },
  { time: 'Live', gateA: 12, gateB: 48, gateC: 29, gateD: 14 },
];

export const PredictionCenter: React.FC = () => {
  const store = useOpsStore();
  const {
    prediction,
    operationsPrediction,
    isLoading,
    error,
    history,
    retry,
    inputPayload,
  } = useCrowdPrediction();
  
  // What-If parameters bound directly to global store
  const sliderAttendance = store.attendance;
  const sliderGateCap = store.gateCapacity;
  const sliderSecurity = store.securityStaff;
  const closeGateC = store.closeGateC;
  const heavyRain = store.heavyRain;
  const vipArrival = store.vipArrival;

  const setSliderAttendance = (val: number) => store.updateWhatIf({ attendance: val });
  const setSliderGateCap = (val: number) => store.updateWhatIf({ gateCapacity: val });
  const setSliderSecurity = (val: number) => store.updateWhatIf({ securityStaff: val });
  const setCloseGateC = (val: boolean) => store.updateWhatIf({ closeGateC: val });
  const setHeavyRain = (val: boolean) => store.updateWhatIf({ heavyRain: val });
  const setVipArrival = (val: boolean) => store.updateWhatIf({ vipArrival: val });

  // ──────────────────────────────────────────────
  // Fallback calculations if API is offline
  // ──────────────────────────────────────────────
  const localCongestionScore = Math.min(
    100,
    Math.max(
      10,
      Math.round(
        (sliderAttendance / 80000) * 68 +
          (100 - sliderGateCap) * 0.45 +
          (closeGateC ? 22 : 0) +
          (heavyRain ? 15 : 0) -
          (sliderSecurity - 300) * 0.06
      )
    )
  );

  const localQueueTime = Math.min(
    60,
    Math.max(
      2,
      Math.round(
        (sliderAttendance / 80000) * 16 * (100 / sliderGateCap) +
          (closeGateC ? 14 : 0) +
          (heavyRain ? 7 : 0) -
          (sliderSecurity - 300) * 0.08
      )
    )
  );

  // Active metrics resolved from Live prediction or fallback local models
  const congestionRisk = prediction ? prediction.congestion_score : localCongestionScore;
  const avgQueueTime = prediction ? prediction.queue_prediction : localQueueTime;
  const predictionConfidence = prediction ? Math.round(prediction.confidence * 100) : 95;
  const riskLevel = prediction ? prediction.risk_level : (congestionRisk > 80 ? 'CRITICAL' : congestionRisk > 60 ? 'HIGH' : 'MEDIUM');

  const maxBy = <T,>(items: T[] | undefined, selector: (item: T) => number): T | undefined =>
    items && items.length > 0
      ? items.reduce((best, item) => (selector(item) > selector(best) ? item : best))
      : undefined;

  const topZone = maxBy(operationsPrediction?.crowd_congestion, item => item.congestion_score);
  const slowestGate = maxBy(operationsPrediction?.queue_times, item => item.estimated_wait_minutes);
  const peakAttendance = maxBy(operationsPrediction?.attendance_forecast, item => item.predicted_attendance);
  const highestRiskZone = operationsPrediction?.crowd_risk.find(item => item.risk_level === 'Critical')
    || operationsPrediction?.crowd_risk.find(item => item.risk_level === 'High')
    || operationsPrediction?.crowd_risk[0];
  const highestMedical = maxBy(operationsPrediction?.medical_demand, item => item.expected_cases);
  const highestVendor = maxBy(operationsPrediction?.vendor_demand, item => item.total_units);
  const fullestParking = maxBy(operationsPrediction?.parking_occupancy, item => item.predicted_occupancy_pct);
  const busiestTraffic = maxBy(
    operationsPrediction?.traffic_flow,
    item => Math.max(item.incoming_congestion, item.outgoing_congestion)
  );
  const primaryRecommendation = operationsPrediction?.recommendations[0];

  const moduleTiles = [
    {
      label: 'Crowd Congestion',
      value: `${topZone?.congestion_score ?? congestionRisk}%`,
      detail: topZone?.zone_name || 'Local zone projection',
      confidence: topZone?.confidence ?? predictionConfidence,
      icon: Users,
      accent: 'text-[#DE638A]',
    },
    {
      label: 'Queue Times',
      value: `${slowestGate?.estimated_wait_minutes ?? avgQueueTime} min`,
      detail: slowestGate?.gate_name || 'Average gate forecast',
      confidence: slowestGate?.confidence ?? predictionConfidence,
      icon: Clock,
      accent: 'text-[#F7B9C4]',
    },
    {
      label: 'Attendance Forecast',
      value: (peakAttendance?.predicted_attendance ?? sliderAttendance).toLocaleString(),
      detail: peakAttendance ? `T+${peakAttendance.hour_offset}h forecast` : 'Live attendance',
      confidence: peakAttendance?.confidence ?? predictionConfidence,
      icon: TrendingUp,
      accent: 'text-[#C6BADE]',
    },
    {
      label: 'Crowd Risk',
      value: highestRiskZone?.risk_level || riskLevel,
      detail: highestRiskZone?.zone_name || 'Local risk band',
      confidence: highestRiskZone?.confidence ?? predictionConfidence,
      icon: AlertTriangle,
      accent: highestRiskZone?.risk_level === 'Critical' ? 'text-red-400' : 'text-orange-400',
    },
    {
      label: 'Emergency Severity',
      value: operationsPrediction?.emergency_severity.predicted_severity || (store.incidents.length > 2 ? 'High' : 'Medium'),
      detail: operationsPrediction?.emergency_severity.incident_type || 'Operational',
      confidence: operationsPrediction?.emergency_severity.confidence ?? predictionConfidence,
      icon: Activity,
      accent: 'text-red-300',
    },
    {
      label: 'Security Resources',
      value: `${operationsPrediction?.security_recommendation.recommended_total_personnel ?? sliderSecurity}`,
      detail: `${operationsPrediction?.security_recommendation.delta ?? 0} staff delta`,
      confidence: operationsPrediction?.security_recommendation.confidence ?? predictionConfidence,
      icon: Shield,
      accent: 'text-emerald-300',
    },
    {
      label: 'Medical Demand',
      value: `${highestMedical?.expected_cases ?? store.incidents.filter(i => i.type.includes('Medical')).length}`,
      detail: highestMedical?.zone_name || 'Current incident load',
      confidence: highestMedical?.confidence ?? predictionConfidence,
      icon: Activity,
      accent: 'text-rose-300',
    },
    {
      label: 'Vendor Demand',
      value: `${highestVendor?.total_units ?? Math.round(sliderAttendance * 0.08)}`,
      detail: highestVendor?.vendor_zone_name || 'Local demand estimate',
      confidence: highestVendor?.confidence ?? predictionConfidence,
      icon: Cpu,
      accent: 'text-amber-300',
    },
    {
      label: 'Parking Occupancy',
      value: `${fullestParking?.predicted_occupancy_pct ?? inputPayload.parking_occupancy}%`,
      detail: fullestParking?.parking_name || 'Parking utilization',
      confidence: fullestParking?.confidence ?? predictionConfidence,
      icon: Activity,
      accent: 'text-sky-300',
    },
    {
      label: 'Traffic Flow',
      value: busiestTraffic
        ? `${Math.max(busiestTraffic.incoming_congestion, busiestTraffic.outgoing_congestion)}%`
        : `${Math.round((sliderAttendance / 80000) * 72)}%`,
      detail: busiestTraffic?.corridor_name || 'Road network pressure',
      confidence: busiestTraffic?.confidence ?? predictionConfidence,
      icon: TrendingUp,
      accent: 'text-blue-300',
    },
    {
      label: 'Weather Impact',
      value: `${operationsPrediction?.weather_impact.operational_risk_impact_pct ?? (heavyRain ? 22 : 4)}%`,
      detail: heavyRain ? 'Storm conditions' : 'Normal conditions',
      confidence: operationsPrediction?.weather_impact.confidence ?? predictionConfidence,
      icon: heavyRain ? CloudRain : Sun,
      accent: heavyRain ? 'text-blue-300' : 'text-yellow-300',
    },
    {
      label: 'Recommendation Engine',
      value: primaryRecommendation?.priority || (congestionRisk > 75 ? 'HIGH' : 'MEDIUM'),
      detail: primaryRecommendation?.title || 'Local mitigation queue',
      confidence: primaryRecommendation?.confidence ?? predictionConfidence,
      icon: CheckCircle,
      accent: 'text-emerald-300',
    },
  ];

  // Dynamic explanation compiler based on variables
  const getAIExplanation = () => {
    let explanation = '';
    if (closeGateC && sliderAttendance > 74000) {
      explanation = `Closing Gate C routes flow onto Gate B. High occupancy (${sliderAttendance.toLocaleString()} spectators) triggers a critical saturation warning.`;
    } else if (heavyRain && congestionRisk > 75) {
      explanation = `Severe storm conditions reduce scanning speed. Large queue bottlenecks forming near underpass corridors.`;
    } else if (congestionRisk > 80) {
      explanation = `Extreme crowd density projects Gate B and A corridors to exceed standard safety bounds within 12 minutes.`;
    } else {
      explanation = `Operations margins stable. Volunteer support is maintaining wait times under 15 minutes.`;
    }
    return explanation;
  };

  // AI recommendations based on live metrics
  const getAIRecommendations = () => {
    const recs = [];
    if (congestionRisk > 75) {
      recs.push({
        title: 'Activate Gate D Overflow Routes',
        priority: 'CRITICAL',
        impact: '-14 min wait time',
        confidence: '95%',
        color: 'text-red-400 bg-red-500/10 border-red-500/20',
      });
    } else {
      recs.push({
        title: 'Open Auxiliary Gate D lanes',
        priority: 'MEDIUM',
        impact: '-4 min wait time',
        confidence: '89%',
        color: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
      });
    }

    if (heavyRain) {
      recs.push({
        title: 'Activate Rain Protection Shelters',
        priority: 'HIGH',
        impact: '+18% concourse capacity',
        confidence: '97%',
        color: 'text-red-400 bg-red-500/10 border-red-500/20',
      });
    }

    recs.push({
      title: `Deploy ${sliderAttendance > 77000 ? '8' : '4'} Concourse Volunters`,
      priority: 'MEDIUM',
      impact: '+12 scan validations/min',
      confidence: '91%',
      color: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
    });

    return recs;
  };

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#DE638A]/20">
      
      {/* Top Header Bar */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6 border-b border-white/5 pb-6">
        <div>
          <div className="flex items-center space-x-2.5">
            <h4 className="text-2xl font-extrabold tracking-tight font-display text-white">
              AI Crowd Prediction Center
            </h4>
            <span className="bg-[#C6BADE]/10 border border-[#C6BADE]/30 text-[#C6BADE] font-bold text-[9px] uppercase tracking-widest px-2.5 py-0.5 rounded-full">
              FastAPI ML Service
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1 font-semibold uppercase tracking-wider">
            Predictive analytics, explainable modeling, and what-if simulation desks
          </p>
        </div>

        {/* Model Meta stats */}
        <div className="flex flex-wrap items-center gap-4 bg-white/[0.02] border border-white/5 px-6 py-3 rounded-2xl backdrop-blur-md text-xs">
          <div className="flex items-center space-x-2 border-r border-white/10 pr-4">
            <span className="text-gray-400 font-bold uppercase tracking-wider text-[10px]">ML SERVICE:</span>
            <span className={`font-bold uppercase ${error ? 'text-red-400' : 'text-emerald-400'}`}>
              {error ? 'OFFLINE' : 'LIVE'}
            </span>
          </div>
          <div className="flex items-center space-x-2 border-r border-white/10 pr-4">
            <span className="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Confidence:</span>
            <span className="font-mono text-[#C6BADE] font-bold">{predictionConfidence}%</span>
          </div>
          <div className="flex items-center space-x-2 pr-2">
            <Clock className="w-3.5 h-3.5 text-[#F7B9C4]" />
            <span className="font-mono text-[#94A3B8]">
              {prediction ? new Date(prediction.timestamp).toLocaleTimeString() : 'Local fallback'}
            </span>
          </div>
          <button
            onClick={() => retry()}
            className="p-1.5 hover:bg-white/5 rounded-lg transition-all"
            title="Force inference check"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[#DE638A]" />
          </button>
        </div>
      </div>

      {/* Connection Failure retry alert bar */}
      {error && (
        <div className="p-4 bg-red-950/45 border border-red-500/25 rounded-2xl flex justify-between items-center text-xs text-red-200">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
            <span><strong>Prediction Service Offline</strong> - Displaying cached math projection values.</span>
          </div>
          <button
            onClick={() => retry()}
            className="px-4 py-1.5 bg-red-500/20 border border-red-500/30 rounded-xl hover:bg-red-500/30 font-bold transition-all uppercase tracking-wider text-[9px]"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Main Layout Grid: Left content block (Sections 1-4) | Right sidebar panel (Recommendations) */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
        
        {/* Main Content Areas (Columns 1-3) */}
        <div className="xl:col-span-3 space-y-8">
          
          {/* Top segment: What-If sliders & ML predictions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* What-If parameters */}
            <div className="glass-panel p-6 rounded-2xl border border-white/5 relative bg-[#231634]/30">
              <div className="flex items-center space-x-2 mb-4 border-b border-white/5 pb-3">
                <Sliders className="w-4 h-4 text-[#DE638A]" />
                <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">What-If Simulation Engine</span>
              </div>

              <div className="space-y-4">
                {/* Attendance Slider */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-300 font-medium">Stadium Attendance</span>
                    <span className="font-bold font-mono text-[#DE638A]">{sliderAttendance.toLocaleString()}</span>
                  </div>
                  <input
                    type="range"
                    min={45000}
                    max={80000}
                    step={100}
                    value={sliderAttendance}
                    onChange={(e) => setSliderAttendance(parseInt(e.target.value))}
                    className="w-full accent-[#DE638A] bg-white/5 h-1.5 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Gate Capacity Slider */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-300 font-medium">Gate Throughput Rate</span>
                    <span className="font-bold font-mono text-[#F7B9C4]">{sliderGateCap}%</span>
                  </div>
                  <input
                    type="range"
                    min={40}
                    max={100}
                    value={sliderGateCap}
                    onChange={(e) => setSliderGateCap(parseInt(e.target.value))}
                    className="w-full accent-[#F7B9C4] bg-white/5 h-1.5 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Security Staff Slider */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-300 font-medium">Security Guards Deployed</span>
                    <span className="font-bold font-mono text-[#C6BADE]">{sliderSecurity} personnel</span>
                  </div>
                  <input
                    type="range"
                    min={200}
                    max={400}
                    value={sliderSecurity}
                    onChange={(e) => setSliderSecurity(parseInt(e.target.value))}
                    className="w-full accent-[#C6BADE] bg-white/5 h-1.5 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Boolean Toggles */}
                <div className="grid grid-cols-3 gap-2.5 pt-2">
                  <button
                    onClick={() => setCloseGateC(!closeGateC)}
                    className={`py-2 px-3 text-[10px] font-bold rounded-xl border transition-all ${
                      closeGateC
                        ? 'border-red-500 text-red-500 bg-red-500/10'
                        : 'border-white/5 text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    Close Gate C
                  </button>

                  <button
                    onClick={() => setHeavyRain(!heavyRain)}
                    className={`py-2 px-3 text-[10px] font-bold rounded-xl border transition-all ${
                      heavyRain
                        ? 'border-blue-400 text-blue-400 bg-blue-400/10'
                        : 'border-white/5 text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    Heavy Rain
                  </button>

                  <button
                    onClick={() => setVipArrival(!vipArrival)}
                    className={`py-2 px-3 text-[10px] font-bold rounded-xl border transition-all ${
                      vipArrival
                        ? 'border-[#F7B9C4] text-[#F7B9C4] bg-[#F7B9C4]/10'
                        : 'border-white/5 text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    VIP Escort
                  </button>
                </div>
              </div>
            </div>

            {/* SECTION 2: ML predictions Card */}
            <div className="glass-panel p-6 rounded-2xl border border-white/5 flex flex-col justify-between relative overflow-hidden">
              <div className="flex items-center space-x-2 border-b border-white/5 pb-3">
                <Cpu className="w-4 h-4 text-[#C6BADE]" />
                <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Live Model Predictions</span>
              </div>

              {isLoading ? (
                <div className="space-y-4 py-8 animate-pulse">
                  <div className="h-4 bg-white/5 rounded w-3/4" />
                  <div className="h-8 bg-white/5 rounded w-1/2" />
                  <div className="h-4 bg-white/5 rounded w-5/6" />
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    {/* Congestion risk */}
                    <div>
                      <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Congestion score</div>
                      <div className="text-lg font-extrabold text-white mt-1 font-mono">{congestionRisk}%</div>
                      <div className="w-full bg-white/5 rounded-full h-1 mt-1.5">
                        <div
                          className={`h-1 rounded-full ${congestionRisk > 75 ? 'bg-red-500' : congestionRisk > 45 ? 'bg-orange-500' : 'bg-emerald-500'}`}
                          style={{ width: `${congestionRisk}%` }}
                        />
                      </div>
                    </div>

                    {/* Queue time */}
                    <div>
                      <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Queue time forecast</div>
                      <div className="text-lg font-extrabold text-white mt-1 font-mono">{avgQueueTime} min</div>
                      <div className="w-full bg-white/5 rounded-full h-1 mt-1.5">
                        <div
                          className="bg-[#DE638A] h-1 rounded-full"
                          style={{ width: `${(avgQueueTime / 60) * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Saturation */}
                    <div>
                      <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Risk level</div>
                      <div className={`text-md font-extrabold mt-1 font-mono ${riskLevel === 'CRITICAL' ? 'text-red-400' : riskLevel === 'HIGH' ? 'text-orange-400' : 'text-[#C6BADE]'}`}>
                        {riskLevel}
                      </div>
                    </div>

                    {/* Confidence */}
                    <div>
                      <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Inference Confidence</div>
                      <div className="text-lg font-extrabold text-white mt-1 font-mono">{predictionConfidence}%</div>
                    </div>
                  </div>

                  <div className="border-t border-white/5 pt-3 mt-4 grid grid-cols-2 gap-2 text-[9.5px] text-[#94A3B8] font-mono">
                    <div>
                      <span>Prediction horizon:</span>
                      <span className="text-white block font-bold">15-45 minutes</span>
                    </div>
                    <div>
                      <span>Timestamp:</span>
                      <span className="text-white block font-bold truncate">
                        {prediction ? new Date(prediction.timestamp).toLocaleTimeString() : 'Local simulation'}
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>

          </div>

          {/* SECTION 1: Live Input Features (Payload overview) */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5">
            <span className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-widest block mb-4">Payload Features Sent to FastAPI</span>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xs">
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold block">Attendance</span>
                <span className="font-extrabold text-white font-mono">{inputPayload.attendance.toLocaleString()}</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold block">Weather</span>
                <span className="font-extrabold text-white font-mono">{heavyRain ? 'Storm (1.0)' : 'Clear (0.1)'}</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold block">Entry Rate</span>
                <span className="font-extrabold text-white font-mono">{inputPayload.entry_rate_per_min} /min</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold block">Metro Arrivals</span>
                <span className="font-extrabold text-white font-mono">{inputPayload.metro_arrivals} /min</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold block">Gate Count</span>
                <span className="font-extrabold text-white font-mono">{inputPayload.gate_open_count} open</span>
              </div>
            </div>
          </div>

          {/* SECTION 2B: Full AI operations model bundle */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-[#C6BADE]" />
                <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">AI Operations Model Registry</span>
              </div>
              <span className="text-[8px] text-[#94A3B8] font-mono uppercase">
                {operationsPrediction ? operationsPrediction.model_version : 'Local fallback projections'}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
              {moduleTiles.map((tile) => {
                const Icon = tile.icon;
                return (
                  <div key={tile.label} className="p-3 bg-[#120A1D]/65 border border-white/5 rounded-xl min-h-[104px] flex flex-col justify-between">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="text-[8px] text-[#94A3B8] font-bold uppercase tracking-wider block">{tile.label}</span>
                        <span className="text-lg text-white font-extrabold font-mono block mt-1">{tile.value}</span>
                      </div>
                      <Icon className={`w-4 h-4 ${tile.accent} shrink-0`} />
                    </div>
                    <div className="pt-2 border-t border-white/[0.04] flex items-center justify-between gap-3 text-[9px]">
                      <span className="text-gray-400 truncate">{tile.detail}</span>
                      <span className="text-[#C6BADE] font-mono font-bold shrink-0">
                        {Math.round(tile.confidence)}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* SECTION 3: Explainable AI */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
            <div className="flex items-center space-x-2 border-b border-white/5 pb-3">
              <AnomalyIcon className="w-4 h-4 text-[#DE638A]" />
              <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Explainable AI (Local Contributions)</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              
              {/* Contribution chart */}
              <div className="space-y-3">
                {isLoading ? (
                  <div className="space-y-4 py-4 animate-pulse">
                    <div className="h-2 bg-white/5 rounded" />
                    <div className="h-2 bg-white/5 rounded" />
                    <div className="h-2 bg-white/5 rounded" />
                  </div>
                ) : (
                  (prediction?.top_factors || [
                    { feature: 'attendance', impact: 57.0 },
                    { feature: 'rain probability', impact: 16.9 },
                    { feature: 'security queue length', impact: 10.8 }
                  ]).map((factor: { feature: string; impact: number }, index: number) => (
                    <div key={index} className="space-y-1">
                      <div className="flex justify-between text-[10px] text-gray-400 font-mono capitalize">
                        <span>{factor.feature}</span>
                        <span className="text-white font-bold">+{factor.impact.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-white/5 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full ${index === 0 ? 'bg-[#DE638A]' : index === 1 ? 'bg-[#F7B9C4]' : 'bg-[#C6BADE]'}`}
                          style={{ width: `${factor.impact}%` }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Explanatory text log */}
              <div className="p-4 bg-[#120A1D] border border-white/5 rounded-2xl flex flex-col justify-between h-full min-h-[160px]">
                <div>
                  <span className="text-[8px] text-[#C6BADE] font-mono uppercase block mb-1">Model Reasoning Log</span>
                  <p className="text-xs text-gray-300 leading-relaxed font-semibold">
                    "{getAIExplanation()}"
                  </p>
                </div>
                
                <span className="text-[8.5px] text-[#94A3B8] font-mono block pt-3 border-t border-white/5">
                  REASONING MATRIX LOADED SUCCESSFULLY
                </span>
              </div>

            </div>
          </div>

          {/* SECTION 4: Prediction History Trend Graph */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
            <span className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-widest block">Model Prediction History Trend</span>
            
            <div className="h-60">
              {history.length < 2 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-xs text-[#94A3B8] border border-dashed border-white/5 rounded-xl">
                  <span>Awaiting inputs. Move the sliders to generate prediction histories and render the comparison curve.</span>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history.map((h, i) => ({
                    time: new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                    score: h.congestion_score,
                    queue: h.queue_prediction
                  }))}>
                    <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" fontSize={9} />
                    <YAxis stroke="rgba(255,255,255,0.3)" fontSize={9} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#231634', borderColor: 'rgba(255,255,255,0.1)' }} />
                    <Legend verticalAlign="top" height={36} />
                    <Line name="Congestion score (%)" type="monotone" dataKey="score" stroke="#DE638A" strokeWidth={2} />
                    <Line name="Queue prediction (min)" type="monotone" dataKey="queue" stroke="#C6BADE" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

        </div>

        {/* Right column: AI Recommendations */}
        <div className="xl:col-span-1 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-white/5 h-full flex flex-col justify-between min-h-[500px]">
            <div>
              <div className="flex items-center space-x-2 border-b border-white/5 pb-4 mb-4">
                <Cpu className="w-4.5 h-4.5 text-[#C6BADE]" />
                <div>
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider font-display">AI Recommendations</h3>
                  <span className="text-[8px] text-[#94A3B8] font-mono">AUTOMATED MITIGATION DESK</span>
                </div>
              </div>

              <div className="space-y-4">
                {getAIRecommendations().map((rec, index) => (
                  <div key={index} className="p-3 bg-[#120A1D]/65 border border-white/5 rounded-xl space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold text-white uppercase font-display">{rec.title}</span>
                      <span className={`text-[7px] font-mono font-bold px-1.5 py-0.25 rounded uppercase border ${rec.color}`}>
                        {rec.priority}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[9px] pt-1 border-t border-white/[0.03]">
                      <span className="text-gray-400">Impact: <span className="text-emerald-400 font-bold font-mono">{rec.impact}</span></span>
                      <span className="text-[#C6BADE] font-bold font-mono">{rec.confidence} confidence</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-white/5 text-[9px] text-[#94A3B8] font-mono text-center flex items-center justify-center space-x-1.5">
              <span>PREDICTIVE LOGIC DESK</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
export default PredictionCenter;
