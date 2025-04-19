// src/components/layouts/MainLayout.js
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Navbar from '../NavBar';
import Footer from '../Footer';

const MainLayout = () => {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar />
      <Container className="flex-grow-1 py-3">
        <Outlet />
      </Container>
      <Footer />
    </div>
  );
};

export default MainLayout;