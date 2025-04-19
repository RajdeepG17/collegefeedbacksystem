// src/components/Sidebar.js
import React from 'react';
import { NavLink } from 'react-router-dom';
import { Nav } from 'react-bootstrap';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { user } = useAuth();
  
  return (
    <div className="sidebar-sticky pt-3">
      <h6 className="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
        <span>Admin Menu</span>
      </h6>
      <Nav className="flex-column">
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/admin" 
            className={({ isActive }) => isActive ? 'active nav-link' : 'nav-link'}
            end
          >
            <i className="fas fa-tachometer-alt me-2"></i>
            Dashboard
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/admin/feedback" 
            className={({ isActive }) => isActive ? 'active nav-link' : 'nav-link'}
          >
            <i className="fas fa-comments me-2"></i>
            Feedbacks
          </Nav.Link>
        </Nav.Item>
        {user?.user_type === 'superadmin' && (
          <Nav.Item>
            <Nav.Link 
              as={NavLink} 
              to="/admin/users" 
              className={({ isActive }) => isActive ? 'active nav-link' : 'nav-link'}
            >
              <i className="fas fa-users me-2"></i>
              User Management
            </Nav.Link>
          </Nav.Item>
        )}
        <Nav.Item>
          <Nav.Link 
            as={NavLink} 
            to="/admin/categories" 
            className={({ isActive }) => isActive ? 'active nav-link' : 'nav-link'}
          >
            <i className="fas fa-list me-2"></i>
            Categories
          </Nav.Link>
        </Nav.Item>
      </Nav>
    </div>
  );
};

export default Sidebar;