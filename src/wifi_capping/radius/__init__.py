"""
freeRADIUS Client Integration
Handles authentication and accounting with freeRADIUS server
"""

import logging
import socket
import time
from typing import Dict, Optional, Tuple

from pyrad import client, dictionary, packet
from pyrad.packet import AuthPacket, AcctPacket

from ..utils.config import Config
from ..utils.security import encrypt_password, validate_credentials


logger = logging.getLogger(__name__)


class RadiusClient:
    """Secure freeRADIUS client for authentication and accounting"""
    
    def __init__(self, config: Config):
        self.config = config
        self.dictionary = dictionary.Dictionary("dictionary")
        
        # Initialize RADIUS client
        self.auth_client = client.Client(
            server=config.radius_host,
            authport=config.radius_auth_port,
            acctport=config.radius_acct_port,
            secret=config.radius_secret.encode('utf-8'),
            dict=self.dictionary
        )
        
        logger.info(f"RADIUS client initialized for server {config.radius_host}")

    def authenticate_user(self, username: str, password: str, 
                         nas_ip: str = None, nas_port: int = None) -> Tuple[bool, Dict]:
        """
        Authenticate user against freeRADIUS server
        
        Args:
            username: User's username
            password: User's password
            nas_ip: Network Access Server IP
            nas_port: Network Access Server port
            
        Returns:
            Tuple of (success: bool, attributes: dict)
        """
        try:
            # Validate input credentials
            if not validate_credentials(username, password):
                logger.warning(f"Invalid credentials format for user {username}")
                return False, {}
            
            # Create authentication request
            req = self.auth_client.CreateAuthPacket(code=packet.AccessRequest)
            req["User-Name"] = username
            req["User-Password"] = req.PwCrypt(password)
            
            # Add NAS information if provided
            if nas_ip:
                req["NAS-IP-Address"] = nas_ip
            if nas_port:
                req["NAS-Port"] = nas_port
                
            # Add additional security attributes
            req["NAS-Identifier"] = "wifi-capping-ncuk"
            req["Service-Type"] = "Framed-User"
            req["Framed-Protocol"] = "PPP"
            
            logger.info(f"Attempting authentication for user: {username}")
            
            # Send authentication request
            reply = self.auth_client.SendPacket(req)
            
            if reply.code == packet.AccessAccept:
                logger.info(f"Authentication successful for user: {username}")
                
                # Extract user attributes from reply
                attributes = {}
                for attr in reply.keys():
                    attributes[attr] = reply[attr][0] if reply[attr] else None
                    
                return True, attributes
                
            elif reply.code == packet.AccessReject:
                logger.warning(f"Authentication failed for user: {username}")
                return False, {}
                
            else:
                logger.error(f"Unexpected RADIUS response code: {reply.code}")
                return False, {}
                
        except Exception as e:
            logger.error(f"RADIUS authentication error for user {username}: {str(e)}")
            return False, {}

    def send_accounting_start(self, username: str, session_id: str, 
                            nas_ip: str, nas_port: int, 
                            user_ip: str = None) -> bool:
        """
        Send accounting start packet to freeRADIUS server
        
        Args:
            username: User's username
            session_id: Unique session identifier
            nas_ip: Network Access Server IP
            nas_port: Network Access Server port
            user_ip: User's assigned IP address
            
        Returns:
            bool: True if accounting start was successful
        """
        try:
            # Create accounting request
            req = self.auth_client.CreateAcctPacket()
            req["Acct-Status-Type"] = "Start"
            req["User-Name"] = username
            req["Acct-Session-Id"] = session_id
            req["NAS-IP-Address"] = nas_ip
            req["NAS-Port"] = nas_port
            req["NAS-Identifier"] = "wifi-capping-ncuk"
            req["Service-Type"] = "Framed-User"
            req["Framed-Protocol"] = "PPP"
            req["Acct-Session-Time"] = 0
            req["Acct-Input-Octets"] = 0
            req["Acct-Output-Octets"] = 0
            
            if user_ip:
                req["Framed-IP-Address"] = user_ip
                
            # Add timestamp
            req["Event-Timestamp"] = int(time.time())
            
            logger.info(f"Sending accounting start for user: {username}, session: {session_id}")
            
            # Send accounting request
            reply = self.auth_client.SendPacket(req)
            
            if reply.code == packet.AccountingResponse:
                logger.info(f"Accounting start successful for session: {session_id}")
                return True
            else:
                logger.error(f"Accounting start failed with code: {reply.code}")
                return False
                
        except Exception as e:
            logger.error(f"Accounting start error for session {session_id}: {str(e)}")
            return False

    def send_accounting_update(self, username: str, session_id: str,
                             session_time: int, input_bytes: int, 
                             output_bytes: int, nas_ip: str, 
                             nas_port: int) -> bool:
        """
        Send accounting update packet with usage statistics
        
        Args:
            username: User's username
            session_id: Unique session identifier
            session_time: Session duration in seconds
            input_bytes: Bytes received by user
            output_bytes: Bytes sent by user
            nas_ip: Network Access Server IP
            nas_port: Network Access Server port
            
        Returns:
            bool: True if accounting update was successful
        """
        try:
            # Create accounting update request
            req = self.auth_client.CreateAcctPacket()
            req["Acct-Status-Type"] = "Interim-Update"
            req["User-Name"] = username
            req["Acct-Session-Id"] = session_id
            req["NAS-IP-Address"] = nas_ip
            req["NAS-Port"] = nas_port
            req["NAS-Identifier"] = "wifi-capping-ncuk"
            req["Service-Type"] = "Framed-User"
            req["Acct-Session-Time"] = session_time
            req["Acct-Input-Octets"] = input_bytes
            req["Acct-Output-Octets"] = output_bytes
            req["Event-Timestamp"] = int(time.time())
            
            logger.debug(f"Sending accounting update for session: {session_id}, "
                        f"time: {session_time}s, in: {input_bytes}B, out: {output_bytes}B")
            
            # Send accounting request
            reply = self.auth_client.SendPacket(req)
            
            if reply.code == packet.AccountingResponse:
                return True
            else:
                logger.error(f"Accounting update failed with code: {reply.code}")
                return False
                
        except Exception as e:
            logger.error(f"Accounting update error for session {session_id}: {str(e)}")
            return False

    def send_accounting_stop(self, username: str, session_id: str,
                           session_time: int, input_bytes: int,
                           output_bytes: int, nas_ip: str,
                           nas_port: int, terminate_cause: str = "User-Request") -> bool:
        """
        Send accounting stop packet when session ends
        
        Args:
            username: User's username
            session_id: Unique session identifier
            session_time: Total session duration in seconds
            input_bytes: Total bytes received by user
            output_bytes: Total bytes sent by user
            nas_ip: Network Access Server IP
            nas_port: Network Access Server port
            terminate_cause: Reason for session termination
            
        Returns:
            bool: True if accounting stop was successful
        """
        try:
            # Create accounting stop request
            req = self.auth_client.CreateAcctPacket()
            req["Acct-Status-Type"] = "Stop"
            req["User-Name"] = username
            req["Acct-Session-Id"] = session_id
            req["NAS-IP-Address"] = nas_ip
            req["NAS-Port"] = nas_port
            req["NAS-Identifier"] = "wifi-capping-ncuk"
            req["Service-Type"] = "Framed-User"
            req["Acct-Session-Time"] = session_time
            req["Acct-Input-Octets"] = input_bytes
            req["Acct-Output-Octets"] = output_bytes
            req["Acct-Terminate-Cause"] = terminate_cause
            req["Event-Timestamp"] = int(time.time())
            
            logger.info(f"Sending accounting stop for user: {username}, session: {session_id}, "
                       f"total time: {session_time}s, total bytes: {input_bytes + output_bytes}")
            
            # Send accounting request
            reply = self.auth_client.SendPacket(req)
            
            if reply.code == packet.AccountingResponse:
                logger.info(f"Accounting stop successful for session: {session_id}")
                return True
            else:
                logger.error(f"Accounting stop failed with code: {reply.code}")
                return False
                
        except Exception as e:
            logger.error(f"Accounting stop error for session {session_id}: {str(e)}")
            return False

    def test_connection(self) -> bool:
        """
        Test connection to freeRADIUS server
        
        Returns:
            bool: True if server is reachable
        """
        try:
            # Test connection with a simple socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.connect((self.config.radius_host, self.config.radius_auth_port))
            sock.close()
            
            logger.info("RADIUS server connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"RADIUS server connection test failed: {str(e)}")
            return False