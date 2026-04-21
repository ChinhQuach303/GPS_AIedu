"use client";

import React from 'react';
import styles from './dashboard.module.css';
import { 
  BarChart3, 
  Activity, 
  Users, 
  BookOpen, 
  Settings,
  ShieldCheck,
  History
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={styles.dashboardContainer}>
      <div className={styles.noiseOverlay}></div>
      
      <div style={{ display: 'flex' }}>
        {/* Sidebar */}
        <aside className={styles.sidebar}>
          <div className={styles.serif} style={{ fontSize: '1.5rem', color: '#D4AF37', marginBottom: '3rem', fontWeight: 700 }}>
            GPS-AIedu
          </div>
          
          <nav style={{ flex: 1 }}>
            <div className={`${styles.navItem} ${styles.navItemActive}`}>
              <Activity size={18} /> Overview
            </div>
            <div className={styles.navItem}>
              <Users size={18} /> Personas
            </div>
            <div className={styles.navItem}>
              <BarChart3 size={18} /> Efficiency
            </div>
            <div className={styles.navItem}>
              <BookOpen size={18} /> Problem Sets
            </div>
            <div className={styles.navItem}>
              <History size={18} /> Session Logs
            </div>
          </nav>
          
          <div style={{ paddingTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <div className={styles.navItem}>
              <ShieldCheck size={18} /> Status: Live
            </div>
            <div className={styles.navItem}>
              <Settings size={18} /> Settings
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main style={{ flex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          {children}
        </main>
      </div>
    </div>
  );
}
