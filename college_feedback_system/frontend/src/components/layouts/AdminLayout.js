// components/layouts/AdminLayout.js
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Container, Row, Col } from 'react-bootstrap';
import NavBar from '../NavBar';
import Sidebar from '../Sidebar';

const AdminLayout = () => {
  return (
    <>
      <NavBar />
      <Container fluid>
        <Row>
          <Col md={3} lg={2} className="bg-light sidebar">
            <Sidebar />
          </Col>
          <Col md={9} lg={10} className="ms-sm-auto px-md-4 py-4">
            <Outlet />
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default AdminLayout;