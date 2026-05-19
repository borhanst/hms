import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, Sequence } from "remotion";
import { MockBrowserFrame, FadeIn, SlideIn } from "./Components";

// Color palette matching HMS theme
const colors = {
  primary: "#4f46e5",
  primaryDark: "#3730a3",
  secondary: "#06b6d4",
  bg: "#0f172a",
  cardBg: "#1e293b",
  sidebarBg: "#1e293b",
  text: "#f8fafc",
  textMuted: "#94a3b8",
  success: "#22c55e",
  warning: "#f59e0b",
  danger: "#ef4444",
  border: "#334155",
};

export const LoginScreen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <MockBrowserFrame url="http://localhost:8000/login/">
      <div
        style={{
          width: "100%",
          height: "100%",
          background: `linear-gradient(135deg, ${colors.bg} 0%, #1a1a3e 100%)`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        <FadeIn delayFrames={10} durationFrames={40}>
          <div
            style={{
              backgroundColor: colors.cardBg,
              borderRadius: 16,
              padding: 40,
              width: 420,
              boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
              border: `1px solid ${colors.border}`,
            }}
          >
            {/* Logo */}
            <div style={{ textAlign: "center", marginBottom: 32 }}>
              <div
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: 16,
                  background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                  margin: "0 auto 16px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 32,
                  color: "white",
                }}
              >
                🏥
              </div>
              <h1
                style={{
                  color: colors.text,
                  fontSize: 28,
                  fontWeight: 700,
                  margin: "0 0 8px",
                }}
              >
                HMS
              </h1>
              <p style={{ color: colors.textMuted, margin: 0, fontSize: 14 }}>
                Hospital Management System
              </p>
            </div>

            {/* Login Form */}
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <div>
                <label
                  style={{
                    color: colors.textMuted,
                    fontSize: 13,
                    marginBottom: 8,
                    display: "block",
                  }}
                >
                  Username
                </label>
                <div
                  style={{
                    backgroundColor: colors.bg,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 8,
                    padding: "12px 16px",
                    color: colors.text,
                    fontSize: 14,
                  }}
                >
                  admin
                </div>
              </div>
              <div>
                <label
                  style={{
                    color: colors.textMuted,
                    fontSize: 13,
                    marginBottom: 8,
                    display: "block",
                  }}
                >
                  Password
                </label>
                <div
                  style={{
                    backgroundColor: colors.bg,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 8,
                    padding: "12px 16px",
                    color: colors.text,
                    fontSize: 14,
                  }}
                >
                  ••••••••••
                </div>
              </div>
              <button
                style={{
                  background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryDark})`,
                  color: "white",
                  border: "none",
                  borderRadius: 8,
                  padding: "14px 24px",
                  fontSize: 16,
                  fontWeight: 600,
                  cursor: "pointer",
                  marginTop: 8,
                }}
              >
                Sign In
              </button>
            </div>

            {/* Demo Credentials */}
            <div
              style={{
                marginTop: 32,
                padding: 16,
                backgroundColor: colors.bg,
                borderRadius: 8,
                border: `1px solid ${colors.border}`,
              }}
            >
              <p
                style={{
                  color: colors.secondary,
                  fontSize: 12,
                  fontWeight: 600,
                  margin: "0 0 12px",
                  textTransform: "uppercase",
                }}
              >
                Demo Accounts
              </p>
              <div
                style={{
                  color: colors.textMuted,
                  fontSize: 12,
                  lineHeight: 1.8,
                }}
              >
                <div>
                  <span style={{ color: colors.success }}>●</span> admin /
                  password123
                </div>
                <div>
                  <span style={{ color: colors.warning }}>●</span>{" "}
                  doctor_john / password123
                </div>
                <div>
                  <span style={{ color: colors.textMuted }}>●</span>{" "}
                  receptionist1 / password123
                </div>
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </MockBrowserFrame>
  );
};

export const DashboardScreen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const statCards = [
    { label: "Total Doctors", value: "3", icon: "👨‍⚕️", color: colors.primary },
    {
      label: "Total Patients",
      value: "6",
      icon: "👥",
      color: colors.secondary,
    },
    {
      label: "Total Reports",
      value: "10",
      icon: "📊",
      color: colors.success,
    },
    {
      label: "Prescriptions",
      value: "8",
      icon: "💊",
      color: colors.warning,
    },
  ];

  return (
    <MockBrowserFrame url="http://localhost:8000/">
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: colors.bg,
          display: "flex",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        {/* Sidebar */}
        <div
          style={{
            width: 240,
            backgroundColor: colors.sidebarBg,
            borderRight: `1px solid ${colors.border}`,
            padding: 24,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 40,
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
              }}
            >
              🏥
            </div>
            <span style={{ color: colors.text, fontWeight: 700, fontSize: 20 }}>
              HMS
            </span>
          </div>

          <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { icon: "📈", label: "Dashboard", active: true },
              { icon: "👨‍⚕️", label: "Doctors" },
              { icon: "👥", label: "Patients" },
              { icon: "📊", label: "Reports" },
              { icon: "💊", label: "Prescriptions" },
              { icon: "👤", label: "Users" },
            ].map((item, i) => (
              <div
                key={item.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: 8,
                  backgroundColor: item.active ? colors.primary : "transparent",
                  color: item.active ? "white" : colors.textMuted,
                  fontSize: 14,
                  fontWeight: item.active ? 600 : 400,
                }}
              >
                <span style={{ fontSize: 16 }}>{item.icon}</span>
                {item.label}
              </div>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: 32, overflow: "hidden" }}>
          <FadeIn delayFrames={10} durationFrames={30}>
            <h1
              style={{
                color: colors.text,
                fontSize: 28,
                fontWeight: 700,
                margin: "0 0 8px",
              }}
            >
              Dashboard
            </h1>
            <p style={{ color: colors.textMuted, margin: "0 0 32px" }}>
              Welcome back, Admin
            </p>
          </FadeIn>

          {/* Stat Cards */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: 20,
              marginBottom: 32,
            }}
          >
            {statCards.map((stat, i) => (
              <FadeIn key={stat.label} delayFrames={20 + i * 5} durationFrames={25}>
                <div
                  style={{
                    backgroundColor: colors.cardBg,
                    borderRadius: 12,
                    padding: 20,
                    border: `1px solid ${colors.border}`,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 12,
                    }}
                  >
                    <span style={{ fontSize: 24 }}>{stat.icon}</span>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: 8,
                        backgroundColor: stat.color + "20",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <span style={{ color: stat.color, fontSize: 14 }}>
                        ↑
                      </span>
                    </div>
                  </div>
                  <div
                    style={{
                      color: colors.textMuted,
                      fontSize: 13,
                      marginBottom: 4,
                    }}
                  >
                    {stat.label}
                  </div>
                  <div
                    style={{
                      color: colors.text,
                      fontSize: 32,
                      fontWeight: 700,
                    }}
                  >
                    {stat.value}
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>

          {/* Charts placeholder */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "2fr 1fr",
              gap: 20,
            }}
          >
            <FadeIn delayFrames={50} durationFrames={30}>
              <div
                style={{
                  backgroundColor: colors.cardBg,
                  borderRadius: 12,
                  padding: 24,
                  border: `1px solid ${colors.border}`,
                  height: 200,
                }}
              >
                <h3
                  style={{
                    color: colors.text,
                    fontSize: 16,
                    margin: "0 0 20px",
                  }}
                >
                  Patient Registrations
                </h3>
                {/* Mock chart */}
                <svg width="100%" height={140} viewBox="0 0 400 140">
                  <defs>
                    <linearGradient
                      id="chartGrad"
                      x1="0%"
                      y1="0%"
                      x2="0%"
                      y2="100%"
                    >
                      <stop
                        offset="0%"
                        stopColor={colors.primary}
                        stopOpacity="0.3"
                      />
                      <stop
                        offset="100%"
                        stopColor={colors.primary}
                        stopOpacity="0"
                      />
                    </linearGradient>
                  </defs>
                  <path
                    d="M 0 100 Q 50 80, 100 90 T 200 60 T 300 70 T 400 40 L 400 140 L 0 140 Z"
                    fill="url(#chartGrad)"
                  />
                  <path
                    d="M 0 100 Q 50 80, 100 90 T 200 60 T 300 70 T 400 40"
                    fill="none"
                    stroke={colors.primary}
                    strokeWidth="3"
                  />
                </svg>
              </div>
            </FadeIn>

            <FadeIn delayFrames={60} durationFrames={30}>
              <div
                style={{
                  backgroundColor: colors.cardBg,
                  borderRadius: 12,
                  padding: 24,
                  border: `1px solid ${colors.border}`,
                  height: 200,
                }}
              >
                <h3
                  style={{
                    color: colors.text,
                    fontSize: 16,
                    margin: "0 0 20px",
                  }}
                >
                  Reports by Category
                </h3>
                {/* Mock donut chart */}
                <svg width={120} height={120} viewBox="0 0 120 120">
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke={colors.border}
                    strokeWidth="16"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke={colors.primary}
                    strokeWidth="16"
                    strokeDasharray="100 314"
                    strokeDashoffset="0"
                    transform="rotate(-90 60 60)"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke={colors.secondary}
                    strokeWidth="16"
                    strokeDasharray="80 314"
                    strokeDashoffset="-100"
                    transform="rotate(-90 60 60)"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke={colors.success}
                    strokeWidth="16"
                    strokeDasharray="60 314"
                    strokeDashoffset="-180"
                    transform="rotate(-90 60 60)"
                  />
                </svg>
              </div>
            </FadeIn>
          </div>
        </div>
      </div>
    </MockBrowserFrame>
  );
};

export const DoctorsScreen: React.FC = () => {
  const doctors = [
    {
      name: "Dr. John Smith",
      spec: "Cardiology",
      dept: "Cardiology",
      fee: "1000 BDT",
      status: "Available",
      avatar: "👨‍⚕️",
    },
    {
      name: "Dr. Sarah Connor",
      spec: "Neurology",
      dept: "Neurology",
      fee: "1200 BDT",
      status: "Available",
      avatar: "👩‍⚕️",
    },
    {
      name: "Dr. Ali Khan",
      spec: "General Medicine",
      dept: "General Medicine",
      fee: "1400 BDT",
      status: "In Surgery",
      avatar: "👨‍⚕️",
    },
  ];

  return (
    <MockBrowserFrame url="http://localhost:8000/doctors/">
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: colors.bg,
          display: "flex",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        {/* Sidebar (simplified) */}
        <div
          style={{
            width: 240,
            backgroundColor: colors.sidebarBg,
            borderRight: `1px solid ${colors.border}`,
            padding: 24,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 40,
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
              }}
            >
              🏥
            </div>
            <span style={{ color: colors.text, fontWeight: 700, fontSize: 20 }}>
              HMS
            </span>
          </div>
          <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { icon: "📈", label: "Dashboard" },
              { icon: "👨‍⚕️", label: "Doctors", active: true },
              { icon: "👥", label: "Patients" },
              { icon: "📊", label: "Reports" },
              { icon: "💊", label: "Prescriptions" },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: 8,
                  backgroundColor: item.active ? colors.primary : "transparent",
                  color: item.active ? "white" : colors.textMuted,
                  fontSize: 14,
                  fontWeight: item.active ? 600 : 400,
                }}
              >
                <span style={{ fontSize: 16 }}>{item.icon}</span>
                {item.label}
              </div>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: 32, overflow: "hidden" }}>
          <FadeIn delayFrames={5} durationFrames={25}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 24,
              }}
            >
              <h1
                style={{
                  color: colors.text,
                  fontSize: 28,
                  fontWeight: 700,
                  margin: 0,
                }}
              >
                Doctors
              </h1>
              <div
                style={{
                  display: "flex",
                  gap: 12,
                }}
              >
                <div
                  style={{
                    backgroundColor: colors.cardBg,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 8,
                    padding: "10px 16px",
                    color: colors.textMuted,
                    fontSize: 14,
                  }}
                >
                  🔍 Search doctors...
                </div>
                <button
                  style={{
                    backgroundColor: colors.primary,
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    padding: "10px 20px",
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  + Add Doctor
                </button>
              </div>
            </div>
          </FadeIn>

          {/* Doctor Cards */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {doctors.map((doc, i) => (
              <FadeIn key={doc.name} delayFrames={15 + i * 8} durationFrames={25}>
                <div
                  style={{
                    backgroundColor: colors.cardBg,
                    borderRadius: 12,
                    padding: 20,
                    border: `1px solid ${colors.border}`,
                    display: "flex",
                    alignItems: "center",
                    gap: 20,
                  }}
                >
                  <div
                    style={{
                      width: 56,
                      height: 56,
                      borderRadius: 12,
                      backgroundColor: colors.primary + "20",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 28,
                    }}
                  >
                    {doc.avatar}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        color: colors.text,
                        fontSize: 18,
                        fontWeight: 600,
                        marginBottom: 4,
                      }}
                    >
                      {doc.name}
                    </div>
                    <div
                      style={{
                        color: colors.textMuted,
                        fontSize: 14,
                        marginBottom: 4,
                      }}
                    >
                      {doc.spec} • {doc.dept}
                    </div>
                    <div
                      style={{
                        color: colors.secondary,
                        fontSize: 14,
                        fontWeight: 600,
                      }}
                    >
                      {doc.fee}
                    </div>
                  </div>
                  <div
                    style={{
                      padding: "6px 16px",
                      borderRadius: 20,
                      backgroundColor:
                        doc.status === "Available"
                          ? colors.success + "20"
                          : colors.warning + "20",
                      color: doc.status === "Available" ? colors.success : colors.warning,
                      fontSize: 13,
                      fontWeight: 600,
                    }}
                  >
                    {doc.status}
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </div>
    </MockBrowserFrame>
  );
};

export const PatientsScreen: React.FC = () => {
  const patients = [
    {
      name: "Kamal Hossain",
      phone: "+880-1712-345678",
      gender: "Male",
      blood: "A+",
      doctor: "Dr. John Smith",
      age: 45,
    },
    {
      name: "Rina Akter",
      phone: "+880-1812-345678",
      gender: "Female",
      blood: "B+",
      doctor: "Dr. Sarah Connor",
      age: 32,
    },
    {
      name: "Rahim Uddin",
      phone: "+880-1912-345678",
      gender: "Male",
      blood: "O+",
      doctor: "Dr. Ali Khan",
      age: 60,
    },
    {
      name: "Fatema Begum",
      phone: "+880-1612-345678",
      gender: "Female",
      blood: "AB+",
      doctor: "Dr. John Smith",
      age: 28,
    },
  ];

  return (
    <MockBrowserFrame url="http://localhost:8000/patients/">
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: colors.bg,
          display: "flex",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        {/* Sidebar */}
        <div
          style={{
            width: 240,
            backgroundColor: colors.sidebarBg,
            borderRight: `1px solid ${colors.border}`,
            padding: 24,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 40,
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
              }}
            >
              🏥
            </div>
            <span style={{ color: colors.text, fontWeight: 700, fontSize: 20 }}>
              HMS
            </span>
          </div>
          <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { icon: "📈", label: "Dashboard" },
              { icon: "👨‍⚕️", label: "Doctors" },
              { icon: "👥", label: "Patients", active: true },
              { icon: "📊", label: "Reports" },
              { icon: "💊", label: "Prescriptions" },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: 8,
                  backgroundColor: item.active ? colors.primary : "transparent",
                  color: item.active ? "white" : colors.textMuted,
                  fontSize: 14,
                  fontWeight: item.active ? 600 : 400,
                }}
              >
                <span style={{ fontSize: 16 }}>{item.icon}</span>
                {item.label}
              </div>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: 32, overflow: "hidden" }}>
          <FadeIn delayFrames={5} durationFrames={25}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 24,
              }}
            >
              <h1
                style={{
                  color: colors.text,
                  fontSize: 28,
                  fontWeight: 700,
                  margin: 0,
                }}
              >
                Patients
              </h1>
              <div
                style={{
                  display: "flex",
                  gap: 12,
                }}
              >
                <div
                  style={{
                    backgroundColor: colors.cardBg,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 8,
                    padding: "10px 16px",
                    color: colors.textMuted,
                    fontSize: 14,
                  }}
                >
                  🔍 Search patients...
                </div>
                <button
                  style={{
                    backgroundColor: colors.primary,
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    padding: "10px 20px",
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  + Add Patient
                </button>
              </div>
            </div>
          </FadeIn>

          {/* Patient Table */}
          <FadeIn delayFrames={20} durationFrames={30}>
            <div
              style={{
                backgroundColor: colors.cardBg,
                borderRadius: 12,
                border: `1px solid ${colors.border}`,
                overflow: "hidden",
              }}
            >
              {/* Table Header */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "2fr 1.5fr 1fr 1fr 1.5fr",
                  padding: "16px 20px",
                  backgroundColor: colors.bg,
                  borderBottom: `1px solid ${colors.border}`,
                  color: colors.textMuted,
                  fontSize: 13,
                  fontWeight: 600,
                  textTransform: "uppercase",
                }}
              >
                <div>Name</div>
                <div>Phone</div>
                <div>Gender</div>
                <div>Blood Group</div>
                <div>Assigned Doctor</div>
              </div>

              {/* Table Rows */}
              {patients.map((patient, i) => (
                <div
                  key={patient.name}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "2fr 1.5fr 1fr 1fr 1.5fr",
                    padding: "16px 20px",
                    borderBottom: `1px solid ${colors.border}`,
                    color: colors.text,
                    fontSize: 14,
                    alignItems: "center",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        borderRadius: 8,
                        backgroundColor: colors.primary + "20",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 16,
                      }}
                    >
                      {patient.gender === "Male" ? "👨" : "👩"}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600 }}>{patient.name}</div>
                      <div style={{ color: colors.textMuted, fontSize: 12 }}>
                        Age {patient.age}
                      </div>
                    </div>
                  </div>
                  <div style={{ color: colors.textMuted }}>{patient.phone}</div>
                  <div>{patient.gender}</div>
                  <div>
                    <span
                      style={{
                        padding: "4px 12px",
                        borderRadius: 12,
                        backgroundColor: colors.danger + "20",
                        color: colors.danger,
                        fontSize: 12,
                        fontWeight: 600,
                      }}
                    >
                      {patient.blood}
                    </span>
                  </div>
                  <div style={{ color: colors.textMuted }}>{patient.doctor}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </div>
    </MockBrowserFrame>
  );
};

export const ReportsScreen: React.FC = () => {
  const reports = [
    {
      test: "Blood Test - CBC",
      patient: "Kamal Hossain",
      category: "Blood",
      status: "Completed",
      date: "Apr 1, 2026",
    },
    {
      test: "Chest X-Ray",
      patient: "Rina Akter",
      category: "X-Ray",
      status: "In Progress",
      date: "Apr 2, 2026",
    },
    {
      test: "MRI Brain Scan",
      patient: "Rahim Uddin",
      category: "MRI",
      status: "Pending",
      date: "Apr 3, 2026",
    },
    {
      test: "Urine Analysis",
      patient: "Fatema Begum",
      category: "Urine",
      status: "Completed",
      date: "Mar 30, 2026",
    },
  ];

  const statusColors: Record<string, string> = {
    Completed: colors.success,
    "In Progress": colors.warning,
    Pending: colors.danger,
  };

  return (
    <MockBrowserFrame url="http://localhost:8000/reports/">
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: colors.bg,
          display: "flex",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        {/* Sidebar */}
        <div
          style={{
            width: 240,
            backgroundColor: colors.sidebarBg,
            borderRight: `1px solid ${colors.border}`,
            padding: 24,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 40,
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
              }}
            >
              🏥
            </div>
            <span style={{ color: colors.text, fontWeight: 700, fontSize: 20 }}>
              HMS
            </span>
          </div>
          <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { icon: "📈", label: "Dashboard" },
              { icon: "👨‍⚕️", label: "Doctors" },
              { icon: "👥", label: "Patients" },
              { icon: "📊", label: "Reports", active: true },
              { icon: "💊", label: "Prescriptions" },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: 8,
                  backgroundColor: item.active ? colors.primary : "transparent",
                  color: item.active ? "white" : colors.textMuted,
                  fontSize: 14,
                  fontWeight: item.active ? 600 : 400,
                }}
              >
                <span style={{ fontSize: 16 }}>{item.icon}</span>
                {item.label}
              </div>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: 32, overflow: "hidden" }}>
          <FadeIn delayFrames={5} durationFrames={25}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 24,
              }}
            >
              <h1
                style={{
                  color: colors.text,
                  fontSize: 28,
                  fontWeight: 700,
                  margin: 0,
                }}
              >
                Diagnostic Reports
              </h1>
              <div
                style={{
                  display: "flex",
                  gap: 12,
                }}
              >
                <div
                  style={{
                    backgroundColor: colors.cardBg,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 8,
                    padding: "10px 16px",
                    color: colors.textMuted,
                    fontSize: 14,
                  }}
                >
                  Filter: All Status
                </div>
                <button
                  style={{
                    backgroundColor: colors.primary,
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    padding: "10px 20px",
                    fontSize: 14,
                    fontWeight: 600,
                  }}
                >
                  + Add Report
                </button>
              </div>
            </div>
          </FadeIn>

          {/* Report Cards */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {reports.map((report, i) => (
              <FadeIn key={report.test} delayFrames={15 + i * 8} durationFrames={25}>
                <div
                  style={{
                    backgroundColor: colors.cardBg,
                    borderRadius: 12,
                    padding: 20,
                    border: `1px solid ${colors.border}`,
                    display: "flex",
                    alignItems: "center",
                    gap: 20,
                  }}
                >
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      borderRadius: 12,
                      backgroundColor: colors.secondary + "20",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 24,
                    }}
                  >
                    📋
                  </div>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        color: colors.text,
                        fontSize: 16,
                        fontWeight: 600,
                        marginBottom: 4,
                      }}
                    >
                      {report.test}
                    </div>
                    <div
                      style={{
                        color: colors.textMuted,
                        fontSize: 14,
                      }}
                    >
                      {report.patient} • {report.date}
                    </div>
                  </div>
                  <div
                    style={{
                      padding: "4px 12px",
                      borderRadius: 8,
                      backgroundColor: colors.primary + "20",
                      color: colors.primary,
                      fontSize: 12,
                      fontWeight: 600,
                    }}
                  >
                    {report.category}
                  </div>
                  <div
                    style={{
                      padding: "6px 16px",
                      borderRadius: 20,
                      backgroundColor: statusColors[report.status] + "20",
                      color: statusColors[report.status],
                      fontSize: 13,
                      fontWeight: 600,
                    }}
                  >
                    {report.status}
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </div>
    </MockBrowserFrame>
  );
};

export const PrescriptionsScreen: React.FC = () => {
  const prescriptions = [
    {
      patient: "Kamal Hossain",
      doctor: "Dr. John Smith",
      diagnosis: "Viral Fever",
      status: "Active",
      date: "Apr 1, 2026",
      medicines: ["Paracetamol 500mg", "Cetirizine 10mg"],
    },
    {
      patient: "Rina Akter",
      doctor: "Dr. Sarah Connor",
      diagnosis: "Migraine",
      status: "Active",
      date: "Mar 28, 2026",
      medicines: ["Ibuprofen 400mg", "Omeprazole 20mg"],
    },
    {
      patient: "Rahim Uddin",
      doctor: "Dr. Ali Khan",
      diagnosis: "Hypertension",
      status: "Completed",
      date: "Mar 25, 2026",
      medicines: ["Amlodipine 5mg"],
    },
  ];

  const statusColors: Record<string, string> = {
    Active: colors.success,
    Completed: colors.textMuted,
    Discontinued: colors.danger,
  };

  return (
    <MockBrowserFrame url="http://localhost:8000/prescriptions/">
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: colors.bg,
          display: "flex",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        }}
      >
        {/* Sidebar */}
        <div
          style={{
            width: 240,
            backgroundColor: colors.sidebarBg,
            borderRight: `1px solid ${colors.border}`,
            padding: 24,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 40,
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
              }}
            >
              🏥
            </div>
            <span style={{ color: colors.text, fontWeight: 700, fontSize: 20 }}>
              HMS
            </span>
          </div>
          <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { icon: "📈", label: "Dashboard" },
              { icon: "👨‍⚕️", label: "Doctors" },
              { icon: "👥", label: "Patients" },
              { icon: "📊", label: "Reports" },
              { icon: "💊", label: "Prescriptions", active: true },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: 8,
                  backgroundColor: item.active ? colors.primary : "transparent",
                  color: item.active ? "white" : colors.textMuted,
                  fontSize: 14,
                  fontWeight: item.active ? 600 : 400,
                }}
              >
                <span style={{ fontSize: 16 }}>{item.icon}</span>
                {item.label}
              </div>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: 32, overflow: "hidden" }}>
          <FadeIn delayFrames={5} durationFrames={25}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 24,
              }}
            >
              <h1
                style={{
                  color: colors.text,
                  fontSize: 28,
                  fontWeight: 700,
                  margin: 0,
                }}
              >
                Prescriptions
              </h1>
              <button
                style={{
                  backgroundColor: colors.primary,
                  color: "white",
                  border: "none",
                  borderRadius: 8,
                  padding: "10px 20px",
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                + Add Prescription
              </button>
            </div>
          </FadeIn>

          {/* Prescription Cards */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {prescriptions.map((rx, i) => (
              <FadeIn key={rx.patient} delayFrames={15 + i * 8} durationFrames={25}>
                <div
                  style={{
                    backgroundColor: colors.cardBg,
                    borderRadius: 12,
                    padding: 24,
                    border: `1px solid ${colors.border}`,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: 16,
                    }}
                  >
                    <div>
                      <div
                        style={{
                          color: colors.text,
                          fontSize: 18,
                          fontWeight: 600,
                          marginBottom: 4,
                        }}
                      >
                        {rx.patient}
                      </div>
                      <div style={{ color: colors.textMuted, fontSize: 14 }}>
                        {rx.doctor} • {rx.date}
                      </div>
                    </div>
                    <div
                      style={{
                        padding: "6px 16px",
                        borderRadius: 20,
                        backgroundColor: statusColors[rx.status] + "20",
                        color: statusColors[rx.status],
                        fontSize: 13,
                        fontWeight: 600,
                      }}
                    >
                      {rx.status}
                    </div>
                  </div>

                  <div
                    style={{
                      backgroundColor: colors.bg,
                      borderRadius: 8,
                      padding: 16,
                      marginBottom: 12,
                    }}
                  >
                    <div
                      style={{
                        color: colors.textMuted,
                        fontSize: 12,
                        marginBottom: 4,
                      }}
                    >
                      Diagnosis
                    </div>
                    <div style={{ color: colors.text, fontSize: 16, fontWeight: 600 }}>
                      {rx.diagnosis}
                    </div>
                  </div>

                  <div>
                    <div
                      style={{
                        color: colors.textMuted,
                        fontSize: 12,
                        marginBottom: 8,
                      }}
                    >
                      Medicines
                    </div>
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      {rx.medicines.map((med) => (
                        <div
                          key={med}
                          style={{
                            backgroundColor: colors.primary + "20",
                            color: colors.primary,
                            padding: "6px 12px",
                            borderRadius: 8,
                            fontSize: 13,
                            fontWeight: 500,
                          }}
                        >
                          💊 {med}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </div>
    </MockBrowserFrame>
  );
};

export const OutroScreen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: `linear-gradient(135deg, ${colors.bg} 0%, #1a1a3e 100%)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      <FadeIn delayFrames={10} durationFrames={40}>
        <div
          style={{
            textAlign: "center",
          }}
        >
          <div
            style={{
              width: 96,
              height: 96,
              borderRadius: 24,
              background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
              margin: "0 auto 24px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 48,
            }}
          >
            🏥
          </div>
          <h1
            style={{
              color: colors.text,
              fontSize: 48,
              fontWeight: 800,
              margin: "0 0 16px",
            }}
          >
            HMS
          </h1>
          <p
            style={{
              color: colors.textMuted,
              fontSize: 20,
              margin: "0 0 40px",
            }}
          >
            Hospital Management System
          </p>
          <div
            style={{
              display: "flex",
              gap: 32,
              justifyContent: "center",
            }}
          >
            {["Django", "HTMX", "Alpine.js", "SQLite"].map((tech) => (
              <div
                key={tech}
                style={{
                  padding: "12px 24px",
                  backgroundColor: colors.cardBg,
                  borderRadius: 12,
                  border: `1px solid ${colors.border}`,
                  color: colors.text,
                  fontSize: 16,
                  fontWeight: 600,
                }}
              >
                {tech}
              </div>
            ))}
          </div>
          <p
            style={{
              color: colors.secondary,
              fontSize: 16,
              marginTop: 48,
              marginBottom: 0,
            }}
          >
            Built with ❤️ for modern healthcare management
          </p>
        </div>
      </FadeIn>
    </div>
  );
};
