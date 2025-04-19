// src/pages/Home.js
import React from 'react';
import { Container } from 'react-bootstrap';

const Home = () => {
  return (
    <Container className="py-5">
      <h1>Welcome to College Feedback System</h1>
      <p className="lead">
        This platform allows students to submit and track feedback about various aspects of college services.
      </p>
    </Container>
  );
};

export default Home;