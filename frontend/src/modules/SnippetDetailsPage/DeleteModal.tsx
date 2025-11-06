import React from 'react';
import './DeleteModal.scss';

type LogOutModalProps = {
  onClose: () => void;
  onDelete: () => void;
}

const DeleteModal: React.FC<LogOutModalProps> = ({ onClose, onDelete }) => {
  return (
    <div className="modalOverlay">
      <div className="modal">
        <h2 className="modalTitle">Are you sure you want to delete this snippet?</h2>
        <div className="modalButtons">
          <button className="modalButton modalButtonCancel" onClick={onClose}>
            Cancel
          </button>
          <button className="modalButton modalButtonLogout" onClick={onDelete}>
            Delete Snippet
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteModal;
