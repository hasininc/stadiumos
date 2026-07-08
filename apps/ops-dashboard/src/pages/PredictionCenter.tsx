import React, { useState, useEffect } from 'react';
import { useOpsStore } from '../store/opsStore';
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

const emergencyRiskData = [
  { time: '17:00', heatRisk: 10, crowdRisk: 15, equipmentRisk: 5 },
  { time: '17:15', heatRisk: 18, crowdRisk: 25, equipmentRisk: 5 },
  { time: '17:30', heatRisk: 30, crowdRisk: 42, equipmentRisk: 12 },
  { time: '17:45', heatRisk: 45, crowdRisk: 60, equipmentRisk: 18 },
  { time: '18:00', heatRisk: 55, crowdRisk: 82, equipmentRisk: 22 },
  { time: 'Live', heatRisk: 68, crowdRisk: 89, equipmentRisk: 15 },
];

export const PredictionCenter: React.FC = () => {
  const store = useOpsStore();
  
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
  // Dynamic Live Input Features (Flips every 4s)
  // ──────────────────────────────────────────────
  const [liveFeatures, setLiveFeatures] = useState({
    entryRate: 450,
    exitRate: 15,
    parkingOccupancy: 81,
    metroRate: 720,
    busRate: 310,
    scanRate: 192,
    securityQueue: 24,
    medicalIncidents: 2,
    foodCourtDensity: 74,
    restroomDensity: 62,
  });

  const [inferenceTime, setInferenceTime] = useState(28);
  const [lastUpdated, setLastUpdated] = useState(0);

  // Auto update live variables slightly to simulate streaming data
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveFeatures((prev) => ({
        entryRate: Math.max(100, Math.min(1000, prev.entryRate + Math.round((Math.random() - 0.5) * 40))),
        exitRate: Math.max(2, Math.min(100, prev.exitRate + Math.round((Math.random() - 0.5) * 6))),
        parkingOccupancy: Math.max(50, Math.min(100, prev.parkingOccupancy + Math.round((Math.random() - 0.5) * 2))),
        metroRate: Math.max(200, Math.min(1500, prev.metroRate + Math.round((Math.random() - 0.5) * 60))),
        busRate: Math.max(50, Math.min(600, prev.busRate + Math.round((Math.random() - 0.5) * 20))),
        scanRate: Math.max(80, Math.min(300, prev.scanRate + Math.round((Math.random() - 0.5) * 15))),
        securityQueue: Math.max(5, Math.min(100, prev.securityQueue + Math.round((Math.random() - 0.5) * 4))),
        medicalIncidents: Math.max(0, Math.min(8, prev.medicalIncidents + (Math.random() > 0.85 ? (Math.random() > 0.5 ? 1 : -1) : 0))),
        foodCourtDensity: Math.max(30, Math.min(99, prev.foodCourtDensity + Math.round((Math.random() - 0.5) * 4))),
        restroomDensity: Math.max(20, Math.min(95, prev.restroomDensity + Math.round((Math.random() - 0.5) * 5))),
      }));
      setInferenceTime(Math.round(24 + Math.random() * 8));
      setLastUpdated(0);
    }, 4000);

    const secondsCounter = setInterval(() => {
      setLastUpdated((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(secondsCounter);
    };
  }, []);

  // ──────────────────────────────────────────────
  // Math Model Projection (Reactions to Sliders)
  // ──────────────────────────────────────────────
  const congestionRisk = Math.min(
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

  const avgQueueTime = Math.min(
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

  const projectedAttendance = Math.round(
    sliderAttendance + (vipArrival ? 150 : 0) - (heavyRain ? 1200 : 0)
  );

  const emergencyRisk = Math.min(
    100,
    Math.max(
      5,
      Math.round(
        (sliderAttendance / 80000) * 22 +
          (heavyRain ? 25 : 0) +
          (closeGateC ? 12 : 0) -
          (sliderSecurity - 300) * 0.04
      )
    )
  );

  const gateSaturation = Math.min(
    100,
    Math.max(
      10,
      Math.round(
        (sliderAttendance / 80000) * 82 * (100 / sliderGateCap) +
          (closeGateC ? 18 : 0)
      )
    )
  );

  const predictionConfidence = Math.min(
    99.8,
    Math.max(
      75.0,
      parseFloat(
        (
          96.4 -
          (closeGateC ? 4.1 : 0) -
          (heavyRain ? 3.2 : 0) +
          (sliderSecurity > 350 ? 1.5 : 0)
        ).toFixed(1)
      )
    )
  );

  // Explainable AI Weight Shares
  const densityWeight = Math.round(31 + (sliderAttendance > 75000 ? 6 : 0) + (heavyRain ? -4 : 0));
  const ticketWeight = Math.round(24 - (sliderGateCap < 80 ? 6 : 0));
  const weatherWeight = heavyRain ? 35 : 12;
  const metroWeight = Math.round(12 + (closeGateC ? 6 : 0));
  const minuteWeight = 9;
  const otherWeight = 100 - (densityWeight + ticketWeight + weatherWeight + metroWeight + minuteWeight);

  // Dynamic explanation compiler
  const getAIExplanation = () => {
    let explanation = '';
    if (closeGateC && sliderAttendance > 74000) {
      explanation = `Closing Gate C routes flow onto Gate B. High occupancy (${sliderAttendance.toLocaleString()} spectators) triggers a critical saturation warning.`;
    } else if (heavyRain && congestionRisk > 75) {
      explanation = `Severe storm conditions reduce scanning speed to ${Math.round(liveFeatures.scanRate * 0.7)} ticket scans/min. Large queue bottlenecks forming near underpass corridors.`;
    } else if (congestionRisk > 80) {
      explanation = `Extreme crowd density coupled with current entry rate (${liveFeatures.entryRate} people/min) projects Gate B and A corridors to exceed standard safety bounds within 12 minutes.`;
    } else {
      explanation = `Operations margins stable. Volunteer support and metro arrival rate (${liveFeatures.metroRate} people/min) are maintaining wait times under 15 minutes.`;
    }
    return explanation;
  };

  // AI recommendations based on projection values
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

    if (emergencyRisk > 50) {
      recs.push({
        title: 'Deploy Medic Standby Squad 3',
        priority: 'HIGH',
        impact: '-3 min response speed',
        confidence: '94%',
        color: 'text-red-400 bg-red-500/10 border-red-500/20',
      });
    }

    recs.push({
      title: 'Notify Transport Authority (Extra trains)',
      priority: 'LOW',
      impact: '+6 metro carriages',
      confidence: '92%',
      color: 'text-[#C6BADE] bg-[#C6BADE]/10 border-[#C6BADE]/20',
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
              CrowdNet v2.1
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1 font-semibold uppercase tracking-wider">
            Predictive analytics, explainable modeling, and what-if simulation desks
          </p>
        </div>

        {/* Model Meta stats */}
        <div className="flex flex-wrap items-center gap-4 bg-white/[0.02] border border-white/5 px-6 py-3 rounded-2xl backdrop-blur-md text-xs">
          <div className="flex items-center space-x-2 border-r border-white/10 pr-4">
            <span className="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Inference:</span>
            <span className="font-mono text-white font-bold">{inferenceTime}ms</span>
          </div>
          <div className="flex items-center space-x-2 border-r border-white/10 pr-4">
            <span className="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Confidence:</span>
            <span className="font-mono text-[#C6BADE] font-bold">{predictionConfidence}%</span>
          </div>
          <div className="flex items-center space-x-2 pr-2">
            <Clock className="w-3.5 h-3.5 text-[#F7B9C4]" />
            <span className="font-mono text-[#94A3B8]">{lastUpdated}s ago</span>
          </div>
          <button
            onClick={() => {
              setInferenceTime(Math.round(22 + Math.random() * 5));
              setLastUpdated(0);
            }}
            className="p-1.5 hover:bg-white/5 rounded-lg transition-all"
            title="Force inference check"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[#DE638A]" />
          </button>
        </div>
      </div>

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

            {/* SECTION 2: ML predictions */}
            <div className="glass-panel p-6 rounded-2xl border border-white/5 flex flex-col justify-between">
              <div className="flex items-center space-x-2 border-b border-white/5 pb-3">
                <Cpu className="w-4 h-4 text-[#C6BADE]" />
                <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Projected Output Predictions</span>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                {/* Congestion risk */}
                <div>
                  <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Congestion Risk</div>
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
                  <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Queue Time</div>
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
                  <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Gate Saturation</div>
                  <div className="text-lg font-extrabold text-white mt-1 font-mono">{gateSaturation}%</div>
                  <div className="w-full bg-white/5 rounded-full h-1 mt-1.5">
                    <div
                      className="bg-[#F7B9C4] h-1 rounded-full"
                      style={{ width: `${gateSaturation}%` }}
                    />
                  </div>
                </div>

                {/* Medical risk */}
                <div>
                  <div className="flex justify-between text-[10px] text-gray-400 uppercase font-semibold">Emergency Index</div>
                  <div className="text-lg font-extrabold text-white mt-1 font-mono">{emergencyRisk}%</div>
                  <div className="w-full bg-white/5 rounded-full h-1 mt-1.5">
                    <div
                      className="bg-amber-500 h-1 rounded-full"
                      style={{ width: `${emergencyRisk}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="border-t border-white/5 pt-3 mt-4 grid grid-cols-3 gap-2 text-[9.5px] text-[#94A3B8] font-mono">
                <div>
                  <span>Horizon:</span>
                  <span className="text-white block font-bold">15-45 min</span>
                </div>
                <div>
                  <span>Peak Influx:</span>
                  <span className="text-white block font-bold">18:25 (HT)</span>
                </div>
                <div>
                  <span>Confidence:</span>
                  <span className="text-white block font-bold">{predictionConfidence}%</span>
                </div>
              </div>
            </div>

          </div>

          {/* SECTION 1: Live Input Features (Streaming data) */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5">
            <span className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-widest block mb-4">Streaming Live Features (Inference Inputs)</span>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Attendance</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{projectedAttendance.toLocaleString()}</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Weather</span>
                <span className="text-sm font-extrabold text-[#F7B9C4] block mt-1 flex items-center space-x-1">
                  {heavyRain ? <CloudRain className="w-3.5 h-3.5 text-blue-400" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
                  <span className="font-mono text-xs">{heavyRain ? 'Storm' : 'Clear'}</span>
                </span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Entry Ingress</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.entryRate} /m</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Metro Arrival</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.metroRate} /m</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Bus Arrival</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.busRate} /m</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Scan Speed</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.scanRate} /m</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Security Queue</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.securityQueue} people</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Emergency Dispatches</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.medicalIncidents} cases</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Food Court Load</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.foodCourtDensity}%</span>
              </div>
              <div className="p-3 bg-white/[0.01] border border-white/[0.03] rounded-xl">
                <span className="text-[8px] text-gray-400 uppercase font-semibold">Restroom Load</span>
                <span className="text-sm font-extrabold text-white block mt-1 font-mono">{liveFeatures.restroomDensity}%</span>
              </div>
            </div>
          </div>

          {/* SECTION 3: Explainable AI (Features & Logic summary) */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
            <div className="flex items-center space-x-2 border-b border-white/5 pb-3">
              <AnomalyIcon className="w-4 h-4 text-[#DE638A]" />
              <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Explainable AI Contribution weights</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              {/* Contribution chart */}
              <div className="space-y-2.5">
                {/* Density weight */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                    <span>Crowd Density</span>
                    <span className="text-white font-bold">+{densityWeight}%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-1.5">
                    <div className="bg-[#DE638A] h-1.5 rounded-full" style={{ width: `${densityWeight}%` }} />
                  </div>
                </div>

                {/* Scan speed weight */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                    <span>Ticket Scan Rate</span>
                    <span className="text-white font-bold">+{ticketWeight}%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-1.5">
                    <div className="bg-[#F7B9C4] h-1.5 rounded-full" style={{ width: `${ticketWeight}%` }} />
                  </div>
                </div>

                {/* Weather weight */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                    <span>Weather Interruption</span>
                    <span className="text-white font-bold">+{weatherWeight}%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-1.5">
                    <div className="bg-blue-400 h-1.5 rounded-full" style={{ width: `${weatherWeight}%` }} />
                  </div>
                </div>

                {/* Metro arrival weight */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                    <span>Metro Arrivals</span>
                    <span className="text-white font-bold">+{metroWeight}%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-1.5">
                    <div className="bg-[#C6BADE] h-1.5 rounded-full" style={{ width: `${metroWeight}%` }} />
                  </div>
                </div>

                {/* Other weight */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                    <span>Other variables</span>
                    <span className="text-white font-bold">+{otherWeight}%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-1.5">
                    <div className="bg-white/20 h-1.5 rounded-full" style={{ width: `${otherWeight}%` }} />
                  </div>
                </div>
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

          {/* SECTION 4: Historical Analytics (Multi-Tab Charts) */}
          <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
            <span className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-widest block">Ingress Forecast & Historical Trends</span>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Chart 1: Attendance Growth */}
              <div className="h-56">
                <span className="text-[9.5px] text-gray-400 uppercase font-mono font-bold block mb-2">Spectator Ingress Growth</span>
                <ResponsiveContainer width="100%" height="90%">
                  <AreaChart data={historicalAttendanceData}>
                    <defs>
                      <linearGradient id="colorAttendance" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#DE638A" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#DE638A" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" fontSize={9} />
                    <YAxis stroke="rgba(255,255,255,0.3)" fontSize={9} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#231634', borderColor: 'rgba(255,255,255,0.1)' }} />
                    <Area type="monotone" dataKey="attendance" stroke="#DE638A" fillOpacity={1} fill="url(#colorAttendance)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Chart 2: Queue Time forecasts */}
              <div className="h-56">
                <span className="text-[9.5px] text-gray-400 uppercase font-mono font-bold block mb-2">Gate Wait Times (mins)</span>
                <ResponsiveContainer width="100%" height="90%">
                  <LineChart data={queueTimeTrendData}>
                    <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" fontSize={9} />
                    <YAxis stroke="rgba(255,255,255,0.3)" fontSize={9} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#231634', borderColor: 'rgba(255,255,255,0.1)' }} />
                    <Line type="monotone" dataKey="gateA" stroke="#DE638A" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="gateB" stroke="#F7B9C4" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="gateC" stroke="#C6BADE" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
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
