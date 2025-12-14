import React from 'react';
import './LogOutModal.scss';

type LogOutModalProps = {
  onClose: () => void;
  onLogout: () => void;
  onLogoutAll: () => void;
}

const LogOutModal: React.FC<LogOutModalProps> = ({ onClose, onLogout, onLogoutAll }) => {
  return (
    <div className="modalOverlay">
      <div className="modal">
        <h2 className="modalTitle">Are you sure you want to log out?</h2>
        <div className="modalButtons">
          <button className="modalButton modalButtonCancel" onClick={onClose}>
            Cancel
          </button>
          <button className="modalButton modalButtonLogout" onClick={onLogout}>
            Log out
          </button>
          <button className="modalButton modalButtonLogoutAll" onClick={onLogoutAll}>
            Log out from all sessions
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogOutModal;
