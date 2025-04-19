// src/components/Footer.js
import React from 'react';
import { Container } from 'react-bootstrap';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-light py-3 mt-auto">
      <Container>
        <p className="text-center text-muted mb-0">
          &copy; {currentYear} College Feedback System. All rights reserved.
        </p>
      </Container>
    </footer>
  );
};

export default Footer;